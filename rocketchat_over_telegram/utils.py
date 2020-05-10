import json
from uuid import uuid4

from click import secho


def uuid() -> str:
    return uuid4().hex

async def send(data, ws):
  data_str = json.dumps(data)
  if '"pong"' not in data_str:
    secho(f"> {data_str}", fg='magenta', bold=True)
  await ws.send(data_str)

async def recv(ws):
  resp = await ws.recv()
  if '"ping"' not in resp:
    secho(f"< {resp}", fg='cyan')
  return json.loads(resp)

def in_available_hours(time):
  return 9 <= time.hour <= 19 and time.weekday() not in [4, 6]
