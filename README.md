# RocketChat over Telegram
Why not! Especially if for some reason you can't use RocketChat's mobile application.

## Installation
```bash
git clone git@github.com/arthur-flam/rocketchat_over_telegram.git
cd rocketchat_over_telegram
pip install .
```

## Setup
1. [Create a telegram bot](https://core.telegram.org/bots#creating-a-new-bot)
2. You need to set some environment variables:


| ENV variable       |  Where to find it                                  |
|--------------------|----------------------------------------------------|
| `ROCKETCHAT_URI`   | the rocket chat server *hostname:port*             |
| `ROCKETCHAT_USER_ID`/`ROCKETCHAT_USER_TOKEN` | Open RocketChat, open the devtools, and in the application data get your `user_id` and `user_token`                                                              |
| `TELEGRAM_BOT_TOKEN` | Telegram gives it to you when you create the bot |
| `TELEGRAM_USERNAME`  | You own telegram username, e.g. `@arthur_flam`   |
| `TELEGRAM_BOTUSER_CHAT_ID` | Start a Telegram chat with your bot, then visit [https://api.telegram.org/bot<yourtoken>/getUpdates](https://api.telegram.org/bot<yourtoken>/getUpdates) to get the chat id.               |


## Usage
```bash
rocketchat_over_telegram
rocketchat_over_telegram --restart-always
```

Now RocketChat messages are sent to you via the Telegram bot. Reply to continue the conversation in the last thread.

## Development
```
pip install --editable .
```

> Merge requests are very welcome!

**Missing features include:**
- Reply-to-message to continue in its thread, not in the last thread.
- Support for multiple users.
- Do a login to RocketChat with the username/password to get the token/user_id.
- Send notifications to telegram in case of auth errors.