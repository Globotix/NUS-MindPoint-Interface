#!/usr/bin/env python
import pika, sys, os
import time

TASK_PUBLISHER_TOPIC = str("TASK_PUBLISHER_TOPIC")
STATUS_TOPIC = str("STATUS_TOPIC")


class AMQPConsumer():
    def __init__(self, hostname):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=str(hostname)))
        self.channel = self.connection.channel()
        
        #Creates a queue, makes sure that it exists
        self.channel.queue_declare(queue=TASK_PUBLISHER_TOPIC)

        self.channel.basic_consume(queue=TASK_PUBLISHER_TOPIC, 
                                    on_message_callback=self.callback, 
                                    auto_ack=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)

class AMQPPublisher():
    def __init__(self, hostname):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=str(hostname)))
        self.channel = self.connection.channel()
        
        #Creates a queue, makes sure that it exists
        self.channel.queue_declare(queue=TASK_PUBLISHER_TOPIC)

        while True:
            self.channel.basic_publish(exchange='', routing_key=TASK_PUBLISHER_TOPIC, body='Hello World!')
            print(" [x] Sent 'Hello World!'")
            time.sleep(1)

def main():
    amqp_publisher = AMQPPublisher('localhost')
    amqp_consumer_ = AMQPConsumer('localhost')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)