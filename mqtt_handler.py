import paho.mqtt.client as mqtt
import json #for parsing json

import pika

from google.protobuf.json_format import MessageToJson, MessageToDict
#Import protobuf messages
import robotTask_pb2


##################################################
#RABBITQ CONSTANTS
##################################################
RABBITMQ_URL = str("amqp://guest:guest@localhost/")
# RABBITMQ_URL = str
TASK_PUBLISHER_TOPIC = str("TASK_PUBLISHER_TOPIC")
STATUS_TOPIC = str("STATUS_TOPIC")

##################################################
#MQTT CONSTANTS
##################################################
# BROKER_ADDRESS = "0.0.0.0" 
# BROKER_PORT = 1883
BROKER_ADDRESS = "52.77.234.153"
BROKER_PORT = "30006"
# MQTT_USER = "guest"
# MQTT_PASSWORD = "guest"
#Subscribed topics
NAVIGATION_TOPIC = "nus5gdt/robots/mindpointeye/navigate"
MARKER_TOPIC = "nus5gdt/robots/mindpointeye/marker"
ROBOT_STATE_TOPIC = "nus5gdt/robots/mindpointeye/robot_state"

class MQTTHandler():
    def __init__(self, broker_address, broker_port, mqtt_user="", mqtt_password=""):
        self.client = mqtt.Client("mqtt_test") #create new instance

        #Set username and password if the user and password fields are not empty
        if (mqtt_user != "" and mqtt_password != ""):
            self.client.username_pw_set(mqtt_user, mqtt_password)

        #Connect to broker
        self.client.connect(broker_address, broker_port, 60) #connect to broker

        #Register callbacks
        self.client.on_connect = self.on_connect
        # self.client.on_log = self.on_log
        # self.client.on_publish = self.on_publish
        self.client.on_disconnnect = self.on_disconnect

        self.client.on_message = self.on_message

        #Subscribe to navigation topic and marker topic
        self.client.subscribe([(NAVIGATION_TOPIC, 0), (MARKER_TOPIC, 0)])

        #Test publishing
        # self.test_pub_mqtt()

    def initAMQPConnection(self, url):
        self.amqp_connection = pika.BlockingConnection(pika.ConnectionParameters(host=str(url)))
        self.channel = self.amqp_connection.channel()
        

    def startLoop(self):
        print("STARTING LOOP")
        self.client.loop_forever()
        # self.client.loop()

    """
    Callback methods for the MQTT client
    """

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

    def on_message(self, client, userdata, msg):
        # print("received msg on topic("+msg.topic+") with msg: "+msg.payload)

        if (msg.topic == NAVIGATION_TOPIC):
            #Convert to protobuf message and send to RabbitMQ
            self.pubNavigate(msg.payload)

        elif (msg.topic == MARKER_TOPIC):
            #Convert to protobuf message and send to RabbitMQ
            self.pubMarker(msg.payload)


    """
    Helper methods
    """
    def createRobotTaskProtobuf(self, uuid, args, task_type, action = 666, order = 666, 
                                level = 3, exec_type = 2, source = 0, require_return = True):
        robot_message = robotTask_pb2.RequestMessage()
        robot_task = robot_message.robotTask.add() #add robot task messsage 

        robot_task.uuid = str(uuid)
        #TOFIX: Remove the /" if it is a problem
        robot_task.args = str(args)
        robot_task.type = task_type

        if (order != 666):
            robot_task.order = order
        if (action != 666):
            robot_task.action = action
        robot_task.level = level
        robot_task.exec_type = exec_type
        robot_task.source = source
        robot_task.require_return = require_return

        return robot_message

    def pubMQTT(self, msg_json, topic):
        """
        Publish a JSON message via MQTT 
        """
        self.client.publish(str(topic), msg_json, 1) #last number is qos (quality of service)


    def pubRabbitMQ(self, msg_json, topic):
        """
        Publish a JSON message via RabbitMQ
        """

        #Creates a queue, makes sure that it exists
        self.channel.queue_declare(queue=topic)

        self.channel.basic_publish(exchange='', routing_key=TASK_PUBLISHER_TOPIC, body=msg_json)
        print(" [x] Sent msg: ", msg_json)



    """
    Publish to Dashboard
    """
    #Process json msg and send to MQTT
    def pubRobotState(self, msg_raw_json):
        """
        Publishes Robot operating state, battery and error to the dashboard

        Message JSON Format:
        {
            "error_message": "",
            "status": "OK",
            "time_stamp": int(time_stamp), # timestamp
            "results": {
                "move_target": "",          # name of target point in movement task
                "move_status": "",          # Status of the executing movement task: idle, running, succeeded, failed, cancelled
                "charge_state": "",         # charging status
                "power_percent": 0.0,       # battery level in %
                "error_code": 0             # error code in hexadecimal，representing by 8 digit in total, if not showing 0, stands for machine are in error.        
                "current_pose": {
                    "x": 0.0,
                    "y": 0.0,
                    "theta": 0.0,
                },
            }
        }

        """

        msg_raw_dict = json.loads(msg_raw_json)

        #1. Create json message
        msg_dict = {}

        results = {}
        #moving status
        results["move_target"] = msg_raw_dict["results"]["move_target"]
        results["move_status"] = msg_raw_dict["results"]["move_status"]

        #Robot states
        results["charge_state"] = msg_raw_dict["results"]["charge_state"]
        results["power_percent"] = msg_raw_dict["results"]["power_percent"]
        results["error_code"] = msg_raw_dict["results"]["error_code"]

        #Robot position
        results["current_pose"] = msg_raw_dict["results"]["current_pose"]

        msg_dict["results"] = results
        msg_dict["error_message"] = str(msg_raw_dict["error_message"])
        msg_dict["status"] = str(msg_raw_dict["status"])
        msg_dict["time_stamp"] = int(msg_raw_dict["time_stamp"])

        msg_json = json.dumps(msg_dict)

        #2. Publish robot state as json msg via MQTT
        self.pubMQTT(msg_json, ROBOT_STATE_TOPIC)

    """
    Publish to Mindpoint
    """
    #Process json msg in protobuf and send to rabbitMQ
    def pubNavigate(self, msg_raw_json):
        #1. Convert from JSON bytes to dictionary
        msg_dict = json.loads(msg_raw_json)
        # msg_dict = msg_raw_json


        #2. Create protobuf message 
        msg_protobuf = robotTask_pb2.RequestMessage()
        msg_args = {}
        if (msg_dict["action"] == "start_movement"):
            msg_args = {"target_marker": msg_dict["target_marker"]}
            msg_args_str = json.dumps(msg_args)

            msg_protobuf = self.createRobotTaskProtobuf(uuid = msg_dict["uuid"], 
                                                        args = msg_args_str, task_type = 0, action = 2)

        elif (msg_dict["action"] == "cancel_movement"):
            msg_args = {"cancel_uuid": msg_dict["cancel_uuid"]}
            msg_args_str = json.dumps(msg_args)
            
            msg_protobuf = self.createRobotTaskProtobuf(uuid = msg_dict["uuid"], 
                                                        args = msg_args_str, task_type = 1, order = 0)
        
        #3. Convert protobuf to JSON
        msg_json = MessageToJson(msg_protobuf)

        #4. Send JSON message over rabbitmq
        self.pubRabbitMQ(msg_json, TASK_PUBLISHER_TOPIC)


    #Process json msg in protobuf and send to rabbitMQ
    def pubMarker(self, msg_raw_json):
        #1. Convert from JSON bytes to dictionary
        msg_dict = json.loads(msg_raw_json)
        # msg_dict = msg_raw_json

        #1. Create protobuf message 
        msg_protobuf = robotTask_pb2.RequestMessage()
        if (msg_dict["action"] == "create_marker"):
            msg_args = {"marker_name": msg_dict["marker_name"], 
                        "x": msg_dict["pos_x"], 
                        "y": msg_dict["pos_y"], 
                        "theta": msg_dict["pos_theta"]}
            msg_args_str = json.dumps(msg_args)

            msg_protobuf = self.createRobotTaskProtobuf(uuid = msg_dict["uuid"], 
                                                        args = msg_args_str, task_type = 1, order = 8)
        
        elif (msg_dict["action"] == "delete_marker"):
            msg_args = {"marker_name": msg_dict["marker_name"]}
            msg_args_str = json.dumps(msg_args)
            
            msg_protobuf = self.createRobotTaskProtobuf(uuid = msg_dict["uuid"], 
                                                        args = msg_args_str, task_type = 1, order = 9)

        #3. Convert protobuf to JSON
        msg_json = MessageToJson(msg_protobuf)

        #4. Send protobuf message over rabbitmq
        self.pubRabbitMQ(msg_json, TASK_PUBLISHER_TOPIC)

    """
    Test methods
    """

    def test_fake_status_msg(self):
        """
        Publishes Robot operating state, battery and error to the dashboard

        Message JSON Format:
        {
            "error_message": "",
            "status": "OK",
            "time_stamp": int(time_stamp), # timestamp
            "results": {
                "move_target": "",          # name of target point in movement task
                "move_status": "",          # Status of the executing movement task: idle, running, succeeded, failed, cancelled
                "charge_state": "",         # charging status
                "power_percent": 0.0,       # battery level in %
                "error_code": 0             # error code in hexadecimal，representing by 8 digit in total, if not showing 0, stands for machine are in error.        
                "current_pose": {
                    "x": 0.0,
                    "y": 0.0,
                    "theta": 0.0,
                },
            }
        }

        """
        msg_dict = {}

        results = {}
        #moving status
        results["move_target"] = "pointA"
        results["move_status"] = "running"

        #Robot states
        results["charge_state"] = str("not charging")
        results["power_percent"] = 58
        results["error_code"] = 0

        #Robot position
        current_pose = {}
        current_pose["x"] = 1.2
        current_pose["y"] = 1.3
        current_pose["theta"] = 1.4
        results["current_pose"] = current_pose

        msg_dict["results"] = results
        msg_dict["error_message"] = str("no errors")
        msg_dict["status"] = str("OK")
        msg_dict["time_stamp"] = int(666)

        #Convert from dict to JSON
        msg_json = json.dumps(msg_dict)

        return msg_json
        
    def test_pub_mqtt(self):
        self.pubRobotState(self.test_fake_status_msg())


