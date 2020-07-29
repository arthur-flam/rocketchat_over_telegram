#!/usr/bin/env python
"""
Forward messages to a better system...


References:
- https://rocket.chat/docs/developer-guides/realtime-api
- https://websockets.readthedocs.io/en/stable/intro.html#installation


## Install
```
pip install websockets
https://github.com/encode/httpx
pip install rocketchat_API
```
"""
import asyncio
from datetime import datetime, timedelta

import websockets
from emoji_data_python import replace_colons
import httpx
import click
from click import secho

from .utils import uuid, send, recv
from .utils import in_available_hours
from .messages import (
  version_msg,
  login_resume_msg,
  sub_stream_notify_user_msg,
  sub_stream_notify_logged_msg,
  sub_stream_room_messages_msg,
  user_presence_msg,
  send_message_msg,
  get_rooms_msg,
  get_subscriptions_msg,
  status_codes,
)
from .auth import rocket_user_id, rocket_user_token, rocket_host, rocket_uri

from .telegram import sendImage, sendMessage as sendTelegram
from .telegram import getUpdates as getUpdatesTelegram



# https://github.com/encode/httpx/issues/859
asyncio.log.logger.setLevel(40)


rocket_ws = None
rocket_last_chat_name = "#chat"
rocket_last_chat_rid = "some-id"


async def startRocketChat():
    global rocket_ws
    global rocket_last_chat_name
    global rocket_last_chat_rid

    last_status_update = datetime.now() - timedelta(hours=1) # anything old
    callbacks = {}
    rooms = [] # {_id, t, name/fname? if t!=d}, ?lastMesage.u.username/name
    # https://rocket.chat/docs/developer-guides/realtime-api/method-calls/get-subscriptions/
    subscriptions = [] # {rid, fname?, name}

    known_messages = { # TODO: limit growth?
      # "id": message,
    }

    async with websockets.connect(rocket_uri) as ws:
        rocket_ws = ws
        await send(version_msg, ws)
        await recv(ws)
        await send(login_resume_msg(rocket_user_token), ws)
        await recv(ws) # server_id...
        await recv(ws) # connected
        await recv(ws) # auth resume

        await send(sub_stream_notify_logged_msg('user-status'), ws)
        await send(sub_stream_notify_user_msg('message'), ws)
        await send(sub_stream_notify_user_msg('notification'), ws)
        await send(sub_stream_notify_user_msg('ort'), ws)
        await send(sub_stream_notify_user_msg('webrtc'), ws)
        await send(sub_stream_room_messages_msg('__my_messages__'), ws)

        msg = get_rooms_msg()
        await send(msg, ws)
        def update_rooms(resp):
          nonlocal rooms
          rooms = resp['result']['update']
        callbacks[msg['id']] = update_rooms

        msg = get_subscriptions_msg()
        await send(msg, ws)
        def update_subscriptions(resp):
          nonlocal subscriptions
          subscriptions = resp['result']['update']
        callbacks[msg['id']] = update_subscriptions


        while True:
          resp = await recv(ws)
          now = datetime.now()

          if resp.get('msg') == "result":
            if resp['id'] in callbacks: 
              callbacks[resp['id']](resp)
            continue

          if resp.get('msg') == "ping":
            await send({"msg": "pong"}, ws)

            long_time_since_update = not last_status_update or now - last_status_update > timedelta(seconds=200)
            should_update_status = long_time_since_update and in_available_hours(now)
            if should_update_status:
              last_status_update = now            
              await send(user_presence_msg('online'), ws)

          if resp.get('msg') == "changed" and resp.get("collection") == "stream-notify-logged" and resp.get('fields')['eventName'] == 'user-status':
            user_id, username, status = resp['fields']['args']
            status = status_codes[status]
            secho('{username}: {status}', fg='blue')

          if resp.get('collection') == 'stream-room-messages':
            messages = resp['fields']['args']
            # https://rocket.chat/docs/developer-guides/realtime-api/the-message-object/
            for m in messages:
              # empty messages are used for images
              if not m.get('rid') or 'msg' not in m:
                continue
              if m.get('t') in ['ul', 'uj', 'au']: # notifications for user left/join, add-user 
                continue
              if m.get('type') in ['subscription-role-added']: # notifications for role: owner/leader... 
                continue
              print(m)

              if m['u']['username'] != 'arthurf': # m.get('unread')
                chat = [chat for chat in subscriptions if m['rid'] == chat['rid']]
                if chat:
                  chat = chat[0]
                  chat_name = chat.get('fname', chat['name']).replace(" ", "")
                else:
                  chat_name = "#NA"
                rocket_last_chat_rid = m['rid']
                # get sub with same rid....
                username = m['u']['username']

                ignore = False
                if m['_id'] not in known_messages:
                  known_messages[m['_id']] = m
                else:
                  # attachments reactions mentions unread alias...
                  previous_message = known_messages[m['_id']]
                  if previous_message['msg'] == m['msg'] and previous_message.get('attachments', '') == m.get('attachments', '') and previous_message.get('reactions', '') == m.get('reactions', ''):
                    ignore = True
                if not ignore:
                  # Reactions format: https://github.com/RocketChat/Rocket.Chat.Android/issues/473
                  if  m.get('reactions'):
                    reactions = "\n<i>nReactions:</i>"
                    for emoji, usernames in m["reactions"].items():
                      usernames = ' & '.join(usernames.get('usernames', []))
                      reactions += f'\n{replace_colons(emoji)}   {usernames}'
                  else:
                    reactions = ''
                  if m.get("attachments"):
                    for attachement in m["attachments"]:
                      if not 'image_url' in attachement:
                        continue
                      headers = {
                        "X-User-Id": rocket_user_id,
                        "X-Auth-Token": rocket_user_token,
                      }
                      image_url = f"http://{rocket_host}{attachement['image_url']}"
                      async with httpx.AsyncClient() as client:
                        r = await client.get(image_url, headers=headers)
                      await sendImage(
                        photo=r.content,
                        file_name=attachement['image_url'].split('/')[-1],
                        file_type=m.get('file', {}).get('type', 'image/png'), # wtf it's not in the attachement itself
                        caption=f"{attachement['title']}\n{attachement['description']}"
                      )
                  # https://core.telegram.org/bots/api#sendphoto
                  notification = f"<u><b>#{chat_name} @{username}:</b></u> {replace_colons(m['msg'])}{reactions}"
                  await sendTelegram(notification)


async def startTelegram():
  while True:
    if not rocket_ws:
      # ideally we should pass the ws instance or await until ready
      await asyncio.sleep(1)

    # https://core.telegram.org/bots/api#update
    updates = await getUpdatesTelegram()
    if updates:
      # https://core.telegram.org/bots/api#message
      for message in updates:
        secho(f'<< [TELEGRAM]: {message}', fg='green', dim=True)
  
        if message.get('reply_to_message'):
           chat = message['reply_to_message']['message']['text']
           # FIXME get chat.rid by matching the room name (__(?P<chat>.*)__)
        else:
           rid = rocket_last_chat_rid
        message = message['message']['text'].replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")
        await send(send_message_msg(message, rid=rid), rocket_ws)

        # TODO: If #chat or @user, start a discussion
        #       for DMs, we may need to call an API to create the room
        #       https://rocket.chat/docs/developer-guides/realtime-api/method-calls/create-direct-message/



def start_forwarder():
  loop = asyncio.get_event_loop()
  futures = asyncio.gather(
    startRocketChat(),
    startTelegram(),
  )
  loop.run_until_complete(futures)


@click.command()
@click.option('--restart-always', is_flag=True)
def start_bot(restart_always):
  if restart_always:
    while True:
      try:
        start_forwarder()
      except Exception as e:
        import traceback
        print(e)
        traceback.print_exc()
        pass
  else:
    start_forwarder()


if __name__ == "__main__":
  start_bot()
