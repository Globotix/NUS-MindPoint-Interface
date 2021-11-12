import asyncio, sys, os, signal
import aio_pika

import json

#Import protobuf messages
import robotTask_pb2

class AMQPHandler():
    def __init__(self):
        self.connection = None
    
    def initParams(self, url, task_publisher_topic, status_topic, task_status_topic, exchange, subscribe_frequency = 0.1):
        self.url = url
        self.queue_name1 = task_publisher_topic
        self.queue_name2 = status_topic
        self.queue_name3 = task_status_topic
        
        self.exchange_name = exchange

        self.subscribe_frequency = subscribe_frequency

    async def initConnection(self, loop):
        print("AMQPConsumer: Init connection")

        self.connection = await aio_pika.connect_robust(\
            self.url, loop=loop)
        # Creating channel from connection
        self.channel = await self.connection.channel()
        # Declaring exchange from channel
        self.exchange = await self.channel.declare_exchange(self.exchange_name, type='topic',durable=True, auto_delete=False)
        
        # Declaring queue from channel
        self.queue1 = await self.channel.declare_queue(self.queue_name1, auto_delete=False) # type: aio_pika.Queue
        self.queue2 = await self.channel.declare_queue(self.queue_name2, auto_delete=False) # type: aio_pika.Queue
        self.queue3 = await self.channel.declare_queue(self.queue_name3, auto_delete=False) # type: aio_pika.Queue

        # Binding queue to exchange for queues
        await self.queue1.bind(self.exchange, self.queue_name1)
        await self.queue2.bind(self.exchange, self.queue_name2)
        await self.queue3.bind(self.exchange, self.queue_name3)

    async def closeConnection(self):
        print("AMQP Connection closing")
        try: 
            await self.connection.close()
            return True
        except Exception as err:
            print("exception while closing AMQP connection: ", err)
            return False

    async def testPublish(self):
        print("AMQPPublisher: test publishing once")
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body='Hello {}'.format(self.queue_name1).encode()
            ),
            routing_key=self.queue_name1
        )
        await self.connection.close()

    async def subscribeQueue(self, routing_key_sub, process_msg_sub = None, act_on_msg = None):
        """
        A recurring loop that checks for any messages being published 
        on the queue corresponding to routing_key_sub. 

        @param routing_key_sub[str]: Routing key identifier for queue being subscribed to.
        @param process_msg_sub[function]: Function processing the incoming(subscribed) message.
        @param act_on_msg[function]: Function converting the outgoing(published) message to an appropriate format.

        """

        print("AMQPHandler: Starting Subscription")

        if routing_key_sub is None:
            print("Please input a routing key to subscribe to")

        while True:
            try:
                #PLEASE DO NOT MAKE THE QUEUE DURABLE
                queue = await self.channel.declare_queue(routing_key_sub, durable=True)
                # await queue.bind(self.exchange, routing_key_sub)
                try: 
                    async with queue.iterator() as queue_iter:
                        async for msg in queue_iter:

                            print(f"subscribeQueue: Received Msg: {msg.body}")
                            #If there is function to process message
                            if process_msg_sub is not None:
                                process_msg_result = await process_msg_sub(msg.body)
                            else:
                                process_msg_result = msg.body

                            await msg.ack() # Acknowledge that message has been received but does not mean that job has been completed

                            if act_on_msg is not None:
                                act_on_msg(process_msg_result)

                except Exception as err:
                    print(f"subscribeQueue: Exception while consuming/processing message: {err} ")
            except aio_pika.exceptions.ChannelClosed as err:
                    print(f"subscribeQueue: Exception while binding to queue: {err} ")
            #A Python AttributeError is raised when you try to call an 
            # attribute of an object whose type does not support that method.
            except AttributeError as err:
                    print(f"subscribeQueue: Exception while binding to queue: {err} ")

            await asyncio.sleep(self.subscribe_frequency)
