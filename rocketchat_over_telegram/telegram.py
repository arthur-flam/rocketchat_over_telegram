from pathlib import Path

from click import secho
# Usually we'd use requests, but here we're making everything async
# the main async HTTP client is aiohttp, but httpx is new and shiny
# https://github.com/encode/httpx
import httpx

from .auth import telegram_bot_token, telegram_user_chat_id

# https://core.telegram.org/bots/api#available-methods
api_prefix = f"https://api.telegram.org/bot{telegram_bot_token}"
uri_revc = f"{api_prefix}/getUpdates"


async def sendMessage(text, chat_id=telegram_user_chat_id):
    secho(f"> {text}", fg="green")
    async with httpx.AsyncClient(verify=False) as client:
        r = await client.post(
            f"{api_prefix}/sendMessage",
            data={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
            },
        )
    secho(f"< {r.json()}", fg="green", bold=True)
    return r.json()


async def sendImage(photo, file_name, file_type, caption, chat_id=telegram_user_chat_id):
    secho(f">[IMG] {file_name}", fg="green")
    files = {'photo': (file_name, photo, file_type)}
    is_animation = 'gif' in file_type
    uri = f"{api_prefix}/sendAnimation" if is_animation else f"{api_prefix}/sendPhoto"
    print(uri)
    async with httpx.AsyncClient(verify=False) as client:
        r = await client.post(
            uri,
            data={
                "chat_id": str(chat_id),
                "caption": caption,
                "parse_mode": "HTML",
            },
            files=files,
        )
    secho(f"< {r.json()}", fg="green", bold=True)
    return r.json()


async def sendDocument(document, file_name, file_type, caption, chat_id=telegram_user_chat_id):
    secho(f">[IMG] {file_name}", fg="green")
    files = {'upload-file': (file_name, photo, file_type)}
    is_animation = 'gif' in file_type
    uri = f"{api_prefix}/sendAnimation" if is_animation else f"{api_prefix}/sendImage"
    async with httpx.AsyncClient(verify=False) as client:
        r = await client.post(
            uri,
            data={
                "chat_id": chat_id,
                "caption": caption,
                "parse_mode": "HTML",
            },
            files=files,
        )
    secho(f"< {r.json()}", fg="green", bold=True)
    return r.json()




data_dir = Path("data")
data_dir.mkdir(exist_ok=True)
last_update_path = Path("data") / "last_update_id.txt"
if not last_update_path.exists():
    last_update_id = 0  # less then any real id
else:
    with last_update_path.open("r") as f:
        last_update_id = int(f.read())


async def getUpdates():
    # https://core.telegram.org/bots/api#getupdates
    global last_update_id
    params = {"offset": last_update_id + 1, "timeout": 20}  # seconds
    async with httpx.AsyncClient(verify=False) as client:
        try:
            r = await client.get(uri_revc, params=params)
        except httpx._exceptions.ReadTimeout:
            return []
    updates = r.json()["result"]
    if not updates:
        return []

    last_update_id = max(u["update_id"] for u in updates)
    with last_update_path.open("w") as f:
        f.write(str(last_update_id))

    return updates


if __name__ == "__main__":
    import asyncio
    msg = asyncio.run(sendMessage("Hello!"))
    print(msg)
