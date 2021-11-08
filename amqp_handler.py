import asyncio, sys, os
import signal

import aio_pika

import paho.mqtt.client as mqtt #import the client1
import json

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
MQTT_USER = "guest"
MQTT_PASSWORD = "guest"
#Subscribed topics
SUB_POSE_TOPIC = "arobot/pose"
SUB_STATE_TOPIC = "arobot/state"
SUB_CMD_TOPIC = "arobot/cmd"
SUB_TASK_TOPIC = "arobot/task"
#Published topics
PUB_CMD_TOPIC = "arobot/cmd/req"
PUB_TASK_TOPIC = "arobot/task/req"


class MQTTHandler():
    def __init__(self, broker_address, broker_port, mqtt_user, mqtt_password):
        self.client = mqtt.Client("mqtt_test") #create new instance

        #Set username and password
        self.client.username_pw_set(mqtt_user, mqtt_password)

        #Connect to broker
        self.client.connect(broker_address, broker_port, 60) #connect to broker

        #Register callbacks
        self.client.on_connect = self.on_connect
        self.client.on_log = self.on_log
        self.client.on_publish = self.on_publish
        self.client.on_disconnnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0: 
            print("Connected to MQTT broker (RC: %s)" % rc)
        else:
            print("Connection to MQTT broker failed (RC: %s)" % rc)

    def on_log(self, client, userdata, level, buf):
        print(buf)

    def on_publish(self, client, userdata, mid):
        print("Data published (Mid: %s)" % mid)

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("Unexpected disconnect")
        print("Disconnected from MQTT broker")

    def publishMsg(self, msg):
        self.client.publish(SUB_POSE_TOPIC, msg, 1) #wtf is the last number

    def pubRobotState(self, error_message, status, time_stamp):
        """
        Publishes Robot operating state, battery and error to the dashboard

        Message JSON Format:
        {
            "error_message": "",
            "status": "OK",
            "time_stamp": int(Time stamp), # timestamp
            "results": {
                "move_target": "",          # name of target point in movement task
                "move_status": "",          # Status of the executing movement task: idle, running, succeeded, failed, cancelled
                "move_retry_times": 0,      # Every increase of the time of retry means the robot has retried one more time on the plath navigation
                "charge_state": "",         # charging status
                "estop_state": True,        # hard_estop_state || soft_estop_state, True-> E stop activated, False-> E stop not activated.
                "control_mode": True,       # In remote controller mode
                "park_mode": True,          # In parking mode
                "control_state": "",        # Control state，auto--auto navigation mode，remote--mannual control mode，control--Remote controller mode
                "power_percent": 0.0,       # battery level in %
                "current_pose": {
                    "x": 0.0,
                    "y": 0.0,
                    "theta": 0.0,
                },
                "error_code": 0             # error code in hexadecimal，representing by 8 digit in total, if not showing 0, stands for machine are in error.        
            }
        }
        """
        sub_state_msg = {}

        result = {}
        #moving status
        result["move_target"] = move_target
        result["move_status"] = move_status
        result["move_retry_times"] = move_retry_times

        #Robot states
        result["charge_state"] = charge_state
        result["estop_state"] = estop_state
        result["control_mode"] = control_mode
        result["park_mode"] = park_mode
        result["control_state"] = control_state
        result["power_percent"] = power_percent
        result["error_code"] = error_code

        #Robot position
        current_pose = {}
        current_pose["x"] = pos_x
        current_pose["y"] = pos_y
        current_pose["theta"] = pos_theta
        result["current_pose"] = current_pose

        sub_state_msg["result"] = result
        sub_state_msg["error_message"] = str(error_message)
        sub_state_msg["status"] = str(status)
        sub_state_msg["time_stamp"] = time_stamp

        sub_state_msg_json = json.dumps(sub_state_msg)

        self.publishMsg(sub_state_msg_json)

    def createMarker(self, uuid, marker_name, pos_x, pos_y, pos_theta, delete=False):
        """
        Example of creating marker message (JSON):
        {
            # Default params
            "type": 1,              #Task type              "order"
            "level: 3,              #Task priority          "IMPORTANT"
            "exec_type": 2,         #Type of task execution  "immediate_exec"
            "source": 0,            #Task creator           "server"
            "order": 8              #Order
            "require_return": True

            # Necessary params
            "uuid": 'ROBOT01_UUID0001',
            "args": '{"marker_name": "pointA", "x": 0.0, "y": 0.0, "theta": 0.0}' ,
        }
        """

        msg = {}

        if (delete):
            #Default Parameters
            msg["type"] = 1         #"order"
            msg["level"] = 3        #"IMPORTANT"
            msg["exec_type"] = 2    #"immediate_exec"
            msg["source"] = 0       #"server" 
            msg["order"] = 9
            msg["require_return"] = True        

            #Necessary Params
            msg["uuid"] = uuid
            args = {}
            args["marker_name"] = marker_name

            msg["args"] = args

        else:
            #Default Parameters
            msg["type"] = 1         #"order"
            msg["level"] = 3        #"IMPORTANT"
            msg["exec_type"] = 2    #"immediate_exec"
            msg["source"] = 0       #"server" 
            msg["order"] = 8 
            msg["require_return"] = True        

            #Necessary Params
            msg["uuid"] = uuid
            args = {}
            args["marker_name"] = marker_name
            args["x"] = pos_x
            args["y"] = pos_y
            args["theta"] = pos_theta

            msg["args"] = args

        return msg

    def pointToPointNavigation(self, uuid, target_marker, cancel=False, cancel_uuid=""):
        """
        Example of PTP Navigation message (JSON):
        {
            # Default params
            "type": 0,              #Task type "action"
            "level: 3,              #Task priority          "IMPORTANT"
            "exec_type": 2,         #Type of task execute   "immediate_exec"
            "source": 0,            #Task creator
            "action": 2,            #Task execute API.      "move_single"
            "require_return": True,

            #Necessary params
            "uuid": 'ROBOT01_UUID0001',
            "args": '{"target_marker": "pointA"}' ,
        }
        """
        msg = {}

        if (cancel):
            #Default Parameters
            msg["type"] = 1                     #"action"
            msg["level"] = 3                    #"IMPORTANT"
            msg["exec_type"] = 2                #"immediate_exec"
            msg["source"] = 0                   #"server" 
            msg["order"] = 0                  
            msg["require_return"] = True        

            #Necessary Params
            args = {}
            args["cancel_uuid"] = cancel_uuid
            msg["uuid"] = uuid

            msg["args"] = args

        else:
            #Default Parameters
            msg["type"] = 0                     #"action"
            msg["level"] = 3                    #"IMPORTANT"
            msg["exec_type"] = 2                #"immediate_exec"
            msg["source"] = 0                   #"server" 
            msg["action"] = 2                   #"move_single"
            msg["require_return"] = True        

            #Necessary Params
            args = {}
            args["target_marker"] = target_marker
            msg["uuid"] = uuid

            msg["args"] = args
        
        return msg

    def subscribeRobotCmd(self, msg):
        """
        Subscribes to robot commands (MQTT) from the dashboard.
        Then converts messages into Protobuf format and sends them
        over rabbitMQ.

        """

        #TODO: Parse the incoming MQTT message
        createMarker(...)
        pointToPointNavigation(...)

        #TODO: Send msg as protobuf via rabbitMQ


class AMQPHandler():
    def __init__(self, url, task_publisher_topic, status_topic):
        self.url = url
        self.queue_name1 = task_publisher_topic
        self.queue_name2 = status_topic

    async def initConnection(self, loop):
        print("AMQPConsumer: Init connection")

        self.mqtt_handler = MQTTHandler(BROKER_ADDRESS, BROKER_PORT, MQTT_USER, MQTT_PASSWORD)

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
            self.log.error(f"closeConnection: Exception received, {err}")
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

    async def publishRobotPose(self, x, y, theta, ts, error):
        self.mqtt_handler.publishRobotPose(x, y, theta, ts, error)

    async def startSubscribing(self):
        print("AMQPHandler: Starting Subscription")

        async with self.connection:
            async with self.queue.iterator() as queue_iter:
                # Cancel consuming after __aexit__
                async for message in queue_iter:
                    async with message.process():
                        print(message.body)

                        # if queue.name in message.body.decode():
                        #     break


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

        loop.create_task(amqp_handler.publishRobotPose(1,1,1,1,"none"))

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


