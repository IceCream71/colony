import asyncio
from lib.colony_py_rpc.lib.RabbitRpc import RabbitRpc

async def add(data):
  return data['first'] + data['second']

async def power(data):
  return data['first'] ** data['second']


async def run():
  client = RabbitRpc()
  await client.init()
  await client.add_handler( 'math.add.py', add)
  await client.add_handler( 'math.power.py', power)

if __name__ == '__main__':
  event_loop = asyncio.get_event_loop()
  event_loop.run_until_complete(run())
  event_loop.run_forever()
