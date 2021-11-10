#!/usr/bin/env python3

from mqtt_handler import *
from amqp_handler import *

import threading

##################################################
#RABBITQ CONSTANTS
##################################################
RABBITMQ_URL = str("amqp://guest:guest@localhost/")
TASK_PUBLISHER_TOPIC = str("TASK_PUBLISHER_TOPIC")
STATUS_TOPIC = str("STATUS_TOPIC")

##################################################
#MQTT CONSTANTS
##################################################
BROKER_ADDRESS = "0.0.0.0" 
BROKER_PORT = 1883
# BROKER_ADDRESS = "52.77.234.153"
# BROKER_PORT = "30006"
MQTT_USER = "guest"
MQTT_PASSWORD = "guest"

MQTT_RABBITMQ_URL = "localhost"
#Subscribed topics

mqtt_handler = MQTTHandler(BROKER_ADDRESS, BROKER_PORT, MQTT_USER, MQTT_PASSWORD)

def start_mqtt():
    print("start_mqtt: Started MQTT Thread")

    mqtt_handler.initAMQPConnection(MQTT_RABBITMQ_URL)
    mqtt_handler.startLoop()

def start_amqp():
    print("start_amqp: Started AMQP Thread")

    #There is no event loop is this is run outside the main thread,
    #so we need to catch the exception and create our own event loop
    try: 
        loop = asyncio.get_event_loop()
    except RuntimeError as ex:
        print(ex)
        print("creating a new event loop")
        loop = asyncio.new_event_loop()

    amqp_handler = AMQPHandler( RABBITMQ_URL, 
                                TASK_PUBLISHER_TOPIC, 
                                STATUS_TOPIC)

    try: 
        loop.create_task(amqp_handler.initConnection(loop))

        loop.create_task(amqp_handler.subscribeQueue(STATUS_TOPIC, act_on_msg=mqtt_handler.pubRobotState))

        loop.run_forever()
    finally:
        print("Event Loop closing")
        loop.close()

class MQTTThread(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        start_mqtt()

class AMQPThread(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        start_amqp()

if __name__ == '__main__':
    try:
        thread1 = MQTTThread(1, "mqtt_thread")
        thread2 = AMQPThread(2, "amqp_thread")

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        print("Main(): all threads ended")
    except KeyboardInterrupt: 
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


