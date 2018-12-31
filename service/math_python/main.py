import asyncio
from lib.colony_py_proto.lib.proto import Proto
import service.math_python.proto.service_pb2 as service_pb2

class Sum(service_pb2.Sum):
  def __init__(self):
    super().__init__()

  async def Calculate(self, data):
    print(data)
    return { 'sum': data.a + data.b }

class Power(service_pb2.Power):
  def __init__(self):
    pass;

  async def Calculate(self):
    pass;

async def run():
  client = Proto()
  await client.init()
  service = Sum()
  client.register_service(service)
  await client.implement( Sum.DESCRIPTOR.full_name + '.Calculate', service.Calculate)

if __name__ == '__main__':
  event_loop = asyncio.get_event_loop()
  event_loop.run_until_complete(run())
  event_loop.run_forever()
