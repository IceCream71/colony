import asyncio
from lib.colony_py_rpc.lib.RabbitRpc import RabbitRpc

async def main():
  client = RabbitRpc()
  await client.init()
  response = await client.call('math:add:py', {'first': 1, 'second': 2})
  print(response)



event_loop = asyncio.get_event_loop()
event_loop.run_until_complete(main())
event_loop.run_forever()
