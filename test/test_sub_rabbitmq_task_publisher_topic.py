"""
Test RabbitMQ subscribing to TASK_PUBLISHER_TOPIC 
"""

#!/usr/bin/env python
import pika, sys, os
import time

import json

RABBITMQ_EXCHANGE = str("default-topic-exchange")

TASK_PUBLISHER_TOPIC = str("TASK_PUBLISHER_TOPIC")
STATUS_TOPIC = str("STATUS_TOPIC")

class AMQPConsumer():
    def __init__(self, hostname):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=str(hostname)))
        self.channel = self.connection.channel()
        
        #create exchange
        self.exchange = self.channel.exchange_declare(exchange=RABBITMQ_EXCHANGE, 
                                                        exchange_type='topic',
                                                        durable=True, auto_delete=False)
        

        #Creates a queue, makes sure that it exists
        self.queue = self.channel.queue_declare(queue=TASK_PUBLISHER_TOPIC, 
                                                durable=True,
                                                auto_delete=False)

        #bind queue to exchange
        self.channel.queue_bind( exchange=RABBITMQ_EXCHANGE, 
                                queue=TASK_PUBLISHER_TOPIC, 
                                routing_key=TASK_PUBLISHER_TOPIC)

        #Consume from queue
        self.channel.basic_consume(queue=TASK_PUBLISHER_TOPIC, 
                                    on_message_callback=self.callback, 
                                    auto_ack=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')

        self.channel.start_consuming()

    def callback(ch, method, properties, body, msg):
        body_dict = json.loads(msg)

        print("AMQPConsumer received: ")
        print( body_dict)


def main():
    amqp_consumer = AMQPConsumer('localhost')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)