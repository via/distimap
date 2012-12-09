import socket
import pika

from simplestore import SimpleStore

class Store:

  def __init__(self):
    self.hostname = socket.gethostname()
    self.backend = SimpleStore()

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    self.channel = connection.channel()
    self.channel.queue_declare(queue='store-%s' % (self.hostname))
    
  def consume(self):
    self.channel.basic_consume(self._request, queue='store-%s' % (self.hostname))
    self.channel.start_consuming()

  def _request(self, chan, method, props, body):
    self.backend.process(body, self._response, props)

  def _response(self, res, props):
    self.channel.basic_publish(exchange='', 
      routing_key=props.reply_to,
      body=res)
      

s = Store()
s.consume()
