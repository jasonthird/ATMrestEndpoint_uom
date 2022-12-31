# example usage and client library for the server

import pika
import uuid
import decimal


class Atm(object):

    def __init__(self, host, port):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, port=port))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, message: object) -> object:
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=message)
        self.connection.process_data_events(time_limit=None)
        return (self.response)

    def withdraw(self, auth, amount):
        message = self.call("withdraw {} {}".format(auth, amount))
        message = message.decode('UTF-8')
        return message

    def deposit(self, auth, amount):
        message = self.call("deposit {} {}".format(auth, amount))
        message = message.decode('UTF-8')
        return message

    def balance(self, auth):
        message = self.call("balance {}".format(auth))
        message = message.decode('UTF-8')
        return message

    def auth(self, username, pin):
        message = self.call("auth {} {}".format(username, pin))
        message = message.decode('UTF-8')
        return message

    def close(self):
        self.connection.close()

""" example usage

atm = Atm()

x = atm.auth("userbbrgf", 8152)
print(x)
print(atm.balance(x))
print(atm.withdraw(x, 100.4213))
print(atm.balance(x))
print(atm.deposit(x, 100))
print(atm.balance(x))
"""