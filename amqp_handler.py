import asyncio, sys, os, signal
import aio_pika

import json

#Import protobuf messages
import robotTask_pb2

##################################################
#RABBITQ CONSTANTS
##################################################
RABBITMQ_URL = str("amqp://guest:guest@localhost/")
TASK_PUBLISHER_TOPIC = str("TASK_PUBLISHER_TOPIC")
STATUS_TOPIC = str("STATUS_TOPIC")


class AMQPHandler():
    def __init__(self, url, task_publisher_topic, status_topic, subscribe_frequency = 0.1):
        self.url = url
        self.queue_name1 = task_publisher_topic
        self.queue_name2 = status_topic

        self.subscribe_frequency = subscribe_frequency

        self.connection = None

    async def initConnection(self, loop):
        print("AMQPConsumer: Init connection")

        self.connection = await aio_pika.connect_robust(\
            self.url, loop=loop)
        # Creating channel from connection
        self.channel = await self.connection.channel()
        # Declaring exchange from channel
        self.exchange = await self.channel.declare_exchange('direct', auto_delete=False)
        # Declaring queue from channel
        self.queue = await self.channel.declare_queue(self.queue_name1, auto_delete=False) # type: aio_pika.Queue

        # Binding queue to exchange for queue_name1
        await self.queue.bind(self.exchange, self.queue_name1)

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

    # async def publishAMQPMsg(self, msg):
    #     await self.exchange.publish(
    #         aio_pika.Message(
    #             bytes('Hello', 'utf-8'),
    #             content_type='text/plain',
    #             headers={'foo': 'bar'}
    #         ),
    #         self.queue_name1
    #     )

    # async def publishMQTTMsg(self, msg):
    #     print("AMQPHandler: publishMQTTMsg")
    #     self.mqtt_handler.publishMsg(msg)

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
                queue = await self.channel.declare_queue(routing_key_sub, durable=False)
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

def main():

    loop = asyncio.get_event_loop()

    amqp_handler = AMQPHandler( RABBITMQ_URL, 
                                TASK_PUBLISHER_TOPIC, 
                                STATUS_TOPIC)

    #signal handling with coroutines
    async def ask_exit(signame, loop):
        """
        Loop should stop here after SIGINT/SIGTERM
        """
        print("got signal %s: exit" % signame)
        await amqp_handler.closeConnection()
        loop.stop()

    #add signal handling for interrupt and termination
    for signame in {'SIGINT', 'SIGTERM'}:
        loop.add_signal_handler(
            #getattr returns value of the named attribute of an object
            getattr(signal, signame),
            #create higher order function
            lambda: asyncio.ensure_future(ask_exit(signame, loop))
        )

    try: 
        loop.create_task(amqp_handler.initConnection(loop))

        loop.run_forever()
    finally:
        print("Loop closing")
        loop.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt: 
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


