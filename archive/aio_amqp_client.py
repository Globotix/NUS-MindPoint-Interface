import asyncio
import aio_pika

RABBITMQ_URL = str("amqp://guest:guest@localhost/")
TASK_PUBLISHER_TOPIC = str("TASK_PUBLISHER_TOPIC")
STATUS_TOPIC = str("STATUS_TOPIC")

class AMQPConsumer():
    def __init__(self, url, task_publisher_topic, status_topic):
        self.url = url
        self.queue_name1 = task_publisher_topic
        self.queue_name2 = status_topic

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

    async def startSubscribing(self):
        print("AMQPConsumer: Starting Subscription")

        async with self.connection:
            async with self.queue.iterator() as queue_iter:
                # Cancel consuming after __aexit__
                async for message in queue_iter:
                    async with message.process():
                        print(message.body)

                        # if queue.name in message.body.decode():
                        #     break

class AMQPPublisher():

    def __init__(self, url, task_publisher_topic, status_topic):
        self.url = url
        self.queue_name1 = task_publisher_topic
        self.queue_name2 = status_topic

    async def initConnection(self, loop):
        print("AMQPPublisher: Init connection")

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

    async def startPublishing(self):
        print("AMQPPublisher: start Publishing")

        await self.exchange.publish(
            aio_pika.Message(
                bytes('Hello', 'utf-8'),
                content_type='text/plain',
                headers={'foo': 'bar'}
            ),
            self.queue_name1
        )

        # await self.channel.default_exchange.publish(
        #     aio_pika.Message(
        #         body='Hello {}'.format(self.queue_name1).encode()
        #     ),
        #     routing_key=self.queue_name1
        # )

        await self.connection.close()


async def main(loop):
    amqp_consumer_ = AMQPConsumer(  RABBITMQ_URL, 
                                    TASK_PUBLISHER_TOPIC, 
                                    STATUS_TOPIC)

    amqp_publisher_ = AMQPPublisher(RABBITMQ_URL, 
                                    TASK_PUBLISHER_TOPIC, 
                                    STATUS_TOPIC)

    await amqp_publisher_.initConnection(loop)
    await amqp_publisher_.startPublishing()

    await amqp_consumer_.initConnection(loop)
    await amqp_consumer_.startSubscribing()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()