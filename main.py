#!/usr/bin/env python3

from mqtt_handler import *
from amqp_handler import *

import threading

import sys, argparse, time


##################################################
#DEFAULT RABBITQ CONSTANTS
##################################################
AIO_RABBITMQ_URL = str("amqp://guest:guest@localhost/")
MQTT_RABBITMQ_URL = str("localhost")

RABBITMQ_EXCHANGE = str("default-topic-exchange")

TASK_PUBLISHER_TOPIC = str("TASK_PUBLISHER_TOPIC")
STATUS_TOPIC = str("STATUS_TOPIC")
TASK_STATUS_TOPIC = str("TASK_STATUS_TOPIC")

##################################################
#DEFAULT MQTT CONSTANTS
##################################################

# MQTT_BROKER_ADDRESS = str("0.0.0.0") 
# MQTT_BROKER_PORT = 1883
# MQTT_USER = "guest"
# MQTT_PASSWORD = "guest"

MQTT_BROKER_ADDRESS = "52.77.234.153"
MQTT_BROKER_PORT = 30006
MQTT_USER = ""
MQTT_PASSWORD = ""

MQTT_NAVIGATION_TOPIC = "nus5gdt/robots/mindpointeye/navigate"
MQTT_MARKER_TOPIC = "nus5gdt/robots/mindpointeye/marker"
MQTT_ROBOT_STATE_TOPIC = "nus5gdt/robots/mindpointeye/robot_state"

mqtt_handler = MQTTHandler()
amqp_handler = AMQPHandler()

#MQTT address and port
mqtt_broker_address = MQTT_BROKER_ADDRESS
mqtt_broker_port = MQTT_BROKER_PORT

#username and password
mqtt_user = MQTT_USER
mqtt_password = MQTT_PASSWORD

#RabbitMQ topics
rabbitmq_exchange = RABBITMQ_EXCHANGE
task_publisher_topic = TASK_PUBLISHER_TOPIC
status_topic = STATUS_TOPIC
task_status_topic = TASK_STATUS_TOPIC

#Digital Twin topics
mqtt_navigation_topic = MQTT_NAVIGATION_TOPIC
mqtt_marker_topic = MQTT_MARKER_TOPIC
mqtt_robot_state_topic = MQTT_ROBOT_STATE_TOPIC

#RabbitMQ address
aio_rabbitmq_url = AIO_RABBITMQ_URL
mqtt_rabbitmq_url = MQTT_RABBITMQ_URL

def parse_arguments():
    parser = argparse.ArgumentParser()

    #MQTT address and port
    parser.add_argument("--mqtt_broker_address", help="Address for MQTT Broker", type=str)
    parser.add_argument("--mqtt_broker_port", help="Port for MQTT Broker", type=int)

    #username and password
    parser.add_argument("--mqtt_user", help="MQTT Broker Username", type=str )
    parser.add_argument("--mqtt_password", help="MQTT Broker Password", type=str)

    #RabbitMQ topics
    parser.add_argument("--task_publisher_topic", help="RabbitMQ Topic for TASK_PUBLISHER_TOPIC", type=str)
    parser.add_argument("--status_topic", help="RabbitMQ Topic for STATUS_TOPIC", type=str)

    #Digital Twin topics
    parser.add_argument("--mqtt_navigation_topic", help="MQTT Topic for navigation", type=str)
    parser.add_argument("--mqtt_marker_topic", help="MQTT Topic for creating marker", type=str)
    parser.add_argument("--mqtt_robot_state_topic", help="RabbitMQ Topic for STATUS_TOPIC", type=str)

    #RabbitMQ address
    parser.add_argument("--aio_rabbitmq_url", help="Async RabbitMQ Address ", type=str)
    parser.add_argument("--mqtt_rabbitmq_url", help="Sync RabbitMQ Address", type=str)

    
    args = parser.parse_args()


    #MQTT address and port
    if args.mqtt_broker_address:
        mqtt_broker_address = args.mqtt_broker_address
    if args.mqtt_broker_port:
        mqtt_broker_port = args.mqtt_broker_port

    #username and password
    if args.mqtt_user:
        mqtt_user =args.mqtt_user
    if args.mqtt_password:
        mqtt_password = args.mqtt_password

    #RabbitMQ topics
    if args.task_publisher_topic:
        task_publisher_topic = args.task_publisher_topic
    if args.status_topic:
        status_topic = args.status_topic

    #Digital Twin topics
    if args.mqtt_navigation_topic:
        mqtt_navigation_topic = args.mqtt_navigation_topic
    if args.mqtt_marker_topic:
        mqtt_marker_topic = args.mqtt_marker_topic
    if args.mqtt_robot_state_topic:
        mqtt_robot_state_topic = args.mqtt_robot_state_topic

    #RabbitMQ Address
    if args.aio_rabbitmq_url:
        aio_rabbitmq_url = args.aio_rabbitmq_url
    if args.mqtt_rabbitmq_url:
        mqtt_rabbitmq_url = args.mqtt_rabbitmq_url


class MQTTThread(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        print("start_mqtt: Started MQTT Thread")

        mqtt_handler.initAMQPParams(task_publisher_topic, status_topic)
        mqtt_handler.initMQTTParams(mqtt_navigation_topic, mqtt_marker_topic, mqtt_robot_state_topic)

        mqtt_handler.initMQTTConnection(mqtt_broker_address, mqtt_broker_port, mqtt_user=mqtt_user, mqtt_password=mqtt_password)
        mqtt_handler.initAMQPConnection(mqtt_rabbitmq_url)
        mqtt_handler.startLoop()

class AMQPThread(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        print("start_amqp: Started AMQP Thread")

        #There is no event loop is this is run outside the main thread,
        #so we need to catch the exception and create our own event loop
        try: 
            loop = asyncio.get_event_loop()
        except RuntimeError as ex:
            print(ex)
            print("creating a new event loop")
            loop = asyncio.new_event_loop()


        amqp_handler.initParams(aio_rabbitmq_url, 
                                task_publisher_topic, 
                                status_topic,
                                task_status_topic,
                                rabbitmq_exchange)

        try: 
            loop.create_task(amqp_handler.initConnection(loop))

            loop.create_task(amqp_handler.subscribeQueue(status_topic, act_on_msg=mqtt_handler.pubRobotState))

            loop.run_forever()
        finally:
            print("Event Loop closing")
            loop.close()

def main():
    thread1 = MQTTThread(1, "mqtt_thread")
    thread2 = AMQPThread(2, "amqp_thread")

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

if __name__ == '__main__':
    try:
        parse_arguments()
        main()

        print("Main(): all threads ended")
    except KeyboardInterrupt: 
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


