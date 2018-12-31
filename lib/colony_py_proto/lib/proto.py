from lib.colony_py_rpc.lib.RabbitRpc import RabbitRpc


class Proto:
  def __init__(self):
    self.client = RabbitRpc()
    self.service = None

  def register_service(self, service):
    self.service = service

  async def init(self):
    await self.client.init()

  async def implement(self, method_name, implementation):
    method_name = method_name.split('.')[-1]
    method = self.service.DESCRIPTOR.FindMethodByName(method_name)
    request_checker = self.service.GetRequestClass(method)()
    response_checker = self.service.GetResponseClass(method)()
    await self.client.add_handler(method.full_name, implementation, request_checker, response_checker)
