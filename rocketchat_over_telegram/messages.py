from .utils import uuid
from .auth import rocket_user_id


status_codes = {
  0: "Offline",
  1: "Online",
  2: "Away",
  3: "Busy",
}

room_types = {
  "d": "Direct chat",
  "c": "Chat",
  "p": "Private chat",
  "l": "Livechat",
}
# room: _id/rid, t


version_msg = {"msg": "connect","version": "1","support": ["1"]}

def login_resume_msg(authToken):
  return {
    "msg": "method",
    "method": "login",
    "id": uuid(),
    "params":[
        { "resume": authToken}
    ]
  }

def sub_stream_notify_user_msg(event):
  return {
    "msg": "sub",
    "id": uuid(),
    "name": "stream-notify-user",
    "params":[
        f"{rocket_user_id}/{event}",
        False,
    ]
  }

def sub_stream_notify_logged_msg(event):
  return {
    "msg": "sub",
    "id": uuid(),
    "name": "stream-notify-logged",
    "params":[
        event,
        False,
    ]
  }

def sub_stream_room_messages_msg(room_id):
  return {
    "msg": "sub",
    "id": uuid(),
    "name": "stream-room-messages",
    "params":[
        room_id,
        False,
    ]
  }

def user_presence_msg(status):
  return {
    "msg": "method",
    "method": f"UserPresence:{status}",
    "id": uuid(),
    "params":[]
  }


def send_message_msg(msg, rid):
  return {
      "msg": "method",
      "method": "sendMessage",
      "id": uuid(),
      "params": [
          {
              "_id": uuid(),
              "rid": rid,
              "msg": msg,
          }
      ]
  }


def get_rooms_msg():
  return {
    "msg": "method",
    "method": "rooms/get",
    "id": uuid(),
    "params": [{
      # latest client update time - to just get changes since last call
      "$date": 0
    }]
  }
def get_subscriptions_msg():
  return {
    "msg": "method",
    "method": "subscriptions/get",
    "id": uuid(),
    "params": [{
      # latest client update time - to just get changes since last call
      "$date": 0
    }]
  }