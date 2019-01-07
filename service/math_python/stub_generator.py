#! /usr/bin/python3

# TODO we need to do something about client, I don't know how for now

import ast, os, sys, imp, astor, inspect

class Ast():
  def __init__(self, compiled_proto_path, class_name):
    self.module = ast.Module(body=[
      ast.Import(names=[
        ast.alias(name=compiled_proto_path, asname=class_name)
      ]),
      ast.Import(names=[
        ast.alias(name='asyncio', asname=None)
      ])
    ])
    self.root_class = ast.ClassDef(name=class_name, body=[], bases=[], decorator_list=[])


  def create_service(self, service_name, body):
    self.root_class.body.append(ast.ClassDef(name=service_name, body=body, bases=[], decorator_list=[]))


  def create_method_handler(self, method, request, response, async=False):
    function_expressions = []
    if async:
      return ast.AsyncFunctionDef(
        name=method.name,
        decorator_list=[],
        args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
        body=[
          ast.Pass()
        ]
      )
    else:
      return ast.FunctionDef(
        name=method.name,
        decorator_list=[],
        args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
        body=[
          ast.Pass()
        ]
      )


  def finish(self):
    self.module.body.append(self.root_class)


  def export(self):
    astor.to_source(stub_ast.module)

def get_service_generated_class(service_module, name):
  for member in inspect.getmembers(service_module):
    if member[0] == name:
      return member[1]

def dynamic_importer(name):
  try:
    fp, pathname, description = imp.find_module(name)
  except ImportError:
    print("unable to locate module: " + name)
    return None

  try:
    imported_package = imp.load_module(name, fp, pathname, description)
  except Exception as e:
    raise e

  # try:
  #   imported_class = None # imp.load_module("%s.%s" % (name, class_name), fp, pathname, description)
  # except Exception as e:
  #   raise(e)

  return imported_package #, imported_class


path = '.'
if len(sys.argv) == 2:
  path = sys.argv[1]


services = []
for file in os.listdir(path):
  if file.endswith('_pb2.py'):
    services.append(file)

"""request = service_pb2.CalculateRequest()
  request.a = 1
  request.b = 2
  response = await client.call('math.Sum.Calculate', request)"""

for service in services:
  service_package = dynamic_importer(os.path.join(path, service.split('.')[0])) # path should be set correctly
  if hasattr(service_package, 'DESCRIPTOR'):
    stub_ast = Ast(service_package.DESCRIPTOR.name, os.path.join(path, service.split('.')[0]))
    proto_services_tuples = service_package.DESCRIPTOR.services_by_name.items()
    for proto_service in proto_services_tuples:
      service_methods = []
      service_name = proto_service[0]
      service_descriptor = proto_service[1]
      service_generated_class = get_service_generated_class(service_package, service_name) # maybe we can find a better solution
      for method in service_descriptor.methods:
        service_methods.append(
          stub_ast.create_method_handler(
            method,
            service_generated_class.GetRequestClass(method),
            service_generated_class.GetResponseClass(method),
            True
          )
        )
      stub_ast.create_service(service_name, service_methods)
    stub_ast.finish()
    stub_ast.export()
