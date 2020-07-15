import thriftpy
from thriftpy.rpc import make_server
from thriftpy.rpc import client_context

messages_thrift = thriftpy.load("messages.thrift", module_name="messages_thrift")
from messages_thrift import Client

def sentMessage(source, destinations, message):
    try:
        with client_context(Client, '127.0.0.1', 6000) as client:
            client.animate(source, destinations, message)
    except:
        return

sentMessage('shard1repl', ['shard2repl'], 'message')