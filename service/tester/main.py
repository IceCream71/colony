import asyncio
from lib.colony_py_rpc.lib.RabbitRpc import RabbitRpc
import service.math_python.proto.service_pb2 as service_pb2

async def main():
  client = RabbitRpc()
  await client.init()
  request = service_pb2.CalculateRequest()
  request.a = 1
  request.b = 2
  response = await client.call('math.Sum.Calculate', request)
  print(response)



event_loop = asyncio.get_event_loop()
event_loop.run_until_complete(main())
event_loop.run_forever()
