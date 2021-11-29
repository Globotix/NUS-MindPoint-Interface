#!/usr/bin/env python3

from mqtt_handler import *
from amqp_handler import *

import threading

import yaml #to parse yaml files

import sys, argparse, time

mqtt_handler = MQTTHandler()
amqp_handler = AMQPHandler()

##################################################
#DEFAULT RABBITQ CONSTANTS
##################################################
aio_rabbitmq_url = ["amqp://guest:guest@localhost/"]
mqtt_rabbitmq_url = ["localhost"]

rabbitmq_exchange = ["default-topic-exchange"]

task_publisher_topic = ["TASK_PUBLISHER_TOPIC"]
status_topic = ["STATUS_TOPIC"]
task_status_topic = ["TASK_STATUS_TOPIC"]

exchange_durable = [False]
task_publisher_topic_durable = [False]
status_topic_durable = [False]
task_status_topic_durable = [False]

##################################################
#DEFAULT MQTT CONSTANTS
##################################################
mqtt_broker_address = ["0.0.0.0"] 
mqtt_broker_port = [1883] 
mqtt_user = ["guest"]
mqtt_password = ["guest"]

mqtt_navigation_topic = ["nus5gdt/robots/mindpointeye/navigate"] 
mqtt_marker_topic = ["nus5gdt/robots/mindpointeye/marker"]
mqtt_robot_state_topic = ["nus5gdt/robots/mindpointeye/robot_state"] 

def parseConfig(config_dir):
    """
    Function to parse YAML file to populate self.state_dictionary

    @param config_dir [string]: Config file directory
    """
    with open(config_dir) as f:
        dataMap = yaml.safe_load(f) # use safe_load instead of load

        #MQTT arguments
        mqtt_broker_address[0] = dataMap["mqtt_broker_address"]
        mqtt_broker_port[0] = dataMap["mqtt_broker_port"]
        mqtt_user[0] = dataMap["mqtt_user"]
        mqtt_password[0] = dataMap["mqtt_password"]

        mqtt_navigation_topic[0] = dataMap["mqtt_navigation_topic"]
        mqtt_marker_topic[0] = dataMap["mqtt_marker_topic"]
        mqtt_robot_state_topic[0] = dataMap["mqtt_robot_state_topic"]

        #RabbitMQ arguments
        aio_rabbitmq_url[0] = dataMap["aio_rabbitmq_url"]
        mqtt_rabbitmq_url[0] = dataMap["mqtt_rabbitmq_url"]

        rabbitmq_exchange[0] = dataMap["rabbitmq_exchange"]

        exchange_durable[0] = dataMap["exchange_durable"]
        task_publisher_topic_durable[0] = dataMap["task_publisher_topic_durable"]
        status_topic_durable[0] = dataMap["status_topic_durable"]
        task_status_topic_durable[0] = dataMap["task_status_topic_durable"]

        task_publisher_topic[0] = dataMap["task_publisher_topic"]
        status_topic[0] = dataMap["status_topic"]
        task_status_topic[0] = dataMap["task_status_topic"]

parseConfig("./config.yaml")

class MQTTThread(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        print("start_mqtt: Started MQTT Thread")

        mqtt_handler.initAMQPParams(task_publisher_topic[0], status_topic[0])
        mqtt_handler.initMQTTParams(mqtt_navigation_topic[0], mqtt_marker_topic[0], mqtt_robot_state_topic[0])

        mqtt_handler.initMQTTConnection(mqtt_broker_address[0], mqtt_broker_port[0], mqtt_user=mqtt_user[0], mqtt_password=mqtt_password[0])
        mqtt_handler.initAMQPConnection(mqtt_rabbitmq_url[0], rabbitmq_exchange[0], exchange_durable[0], task_publisher_topic_durable[0], status_topic_durable[0], task_status_topic_durable[0])
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


        amqp_handler.initParams(aio_rabbitmq_url[0], 
                                task_publisher_topic[0], 
                                status_topic[0],
                                task_status_topic[0],
                                rabbitmq_exchange[0], 
                                exchange_durable[0], 
                                task_publisher_topic_durable[0], status_topic_durable[0], task_status_topic_durable[0]
                                )

        try: 
            loop.create_task(amqp_handler.initConnection(loop))

            loop.create_task(amqp_handler.subscribeQueue(status_topic[0], act_on_msg=mqtt_handler.pubRobotState))

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
        main()

        print("Main(): all threads ended")
    except KeyboardInterrupt: 
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


