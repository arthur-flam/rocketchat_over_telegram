import os

rocket_host = os.environ['ROCKETCHAT_URI']
rocket_uri = f"ws://{rocket_host}/websocket"
# read them from the web-based app
rocket_user_id = os.environ['ROCKETCHAT_USER_ID']
rocket_user_token = os.environ['ROCKETCHAT_USER_TOKEN']

telegram_bot_token = os.environ['TELEGRAM_BOT_TOKEN']
telegram_username = os.environ['TELEGRAM_USERNAME']
# the chat ID is read from the logs when the bot recieves messages
telegram_user_chat_id = int(os.environ['TELEGRAM_BOTUSER_CHAT_ID'])
