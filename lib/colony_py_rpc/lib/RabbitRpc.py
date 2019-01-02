import asyncio
import aio_pika
import random
from lib.colony_py_rpc.lib.Rpc import Rpc
import dict_to_protobuf

class Job:
  def __init__(self, handler, queue_name, publisher, request_class, response_class):
    self.handler = handler
    self.queue_name = queue_name
    self.publisher = publisher
    self.request_class = request_class
    self.response_class = response_class


  def generate_response(self, result):
    response = self.response_class()
    dict_to_protobuf.parse_dict(result, response)
    return response.SerializeToString()


  async def process_incoming_message(self, message: aio_pika.IncomingMessage):
    request_payload = message.body
    request = None
    if self.request_class:
      request = self.request_class()
      request.ParseFromString(request_payload)
    else:
      request = eval(request_payload.decode())

    result = await self.handler(request)

    if self.response_class:
      result = self.generate_response(result)
    else:
      result = str(result).encode()

    await self.publisher.default_exchange.publish(
      aio_pika.Message(
        body=result,
        correlation_id=message.correlation_id
      ),
      routing_key=message.reply_to,
    )
    message.ack()

class ResponseManager:
  def __init__(self):
    self.locks = dict()
    self.resps = dict()

  def add_response(self, correlation_id, message):
    self.resps[correlation_id] = message
    if correlation_id in self.locks:
      self.locks[correlation_id].set()

  async def get_response(self, correlation_id):
    if correlation_id in self.resps:
      res = self.resps[correlation_id]
      self.resps.pop(correlation_id)
      return res

    # Add a timeout mechanism

    event = asyncio.Event()
    self.locks[correlation_id] = event
    await event.wait()
    res = self.resps[correlation_id]

    # clean up
    self.locks.pop(correlation_id)
    self.resps.pop(correlation_id)

    return res

class RabbitRpc(Rpc):
  def __init__(self):
    super().__init__()
    self.response_handlers = {}
    self.response_manager = ResponseManager()
    self.connection = None
    self.resQueue = None
    self.channel = None


  @staticmethod
  def __generate_uuid():
    return repr(random.random()) + repr(random.random()) + repr(random.random())

  async def __response_handler(self, message: aio_pika.IncomingMessage):
    with message.process():
      self.response_manager.add_response(
        message.correlation_id.decode(),
        message.body.decode()
      )

  async def init(self):
    self.connection = await aio_pika.connect_robust(
      "amqp://localhost"
    )
    self.channel = await self.connection.channel()
    await self.channel.set_qos(prefetch_count=5)
    self.resQueue = await self.channel.declare_queue("", auto_delete=True)
    await self.resQueue.consume(self.__response_handler)
    return self.connection

  async def add_handler(self, queue_name, handler, request_class=None, response_class=None):
    new_queue = await self.channel.declare_queue(queue_name, auto_delete=True) # TODO, We have to remove it
    job_handler = Job(handler, queue_name, self.channel, request_class, response_class)
    await new_queue.consume(job_handler.process_incoming_message)


  async def call(self, queue_name, data):
    correlation_id = self.__generate_uuid()
    if callable(data.SerializeToString):
      data = data.SerializeToString()
    else:
      data = str(data).encode()
    await self.channel.default_exchange.publish(
      aio_pika.Message(
        body=data,
        correlation_id=correlation_id,
        reply_to=self.resQueue.name
      ),
      routing_key=queue_name
    )
    response = await self.response_manager.get_response(correlation_id)
    return response

