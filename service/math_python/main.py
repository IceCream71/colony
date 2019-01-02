import asyncio
from lib.colony_py_proto.lib.proto import Proto
import service.math_python.proto.service_pb2 as service_pb2


async def Calculate(data):
  print(data)
  return { 'sum': data.a + data.b }

# class Sum(service_pb2.Sum):
#   def __init__(self):
#     super().__init__()
#
#   async def Calculate(self, data):
#     print(data)
#     return { 'sum': data.a + data.b }


async def run():
  client = Proto()
  await client.init()
  service = service_pb2.Sum()
  client.register_service(service)
  await client.implement( service.DESCRIPTOR.full_name + '.Calculate', Calculate)

if __name__ == '__main__':
  event_loop = asyncio.get_event_loop()
  event_loop.run_until_complete(run())
  event_loop.run_forever()
