import sys, argparse

##################################################
#RABBITQ CONSTANTS
##################################################
AIO_RABBITMQ_URL = str("amqp://guest:guest@localhost/")
MQTT_RABBITMQ_URL = "localhost"
TASK_PUBLISHER_TOPIC = str("TASK_PUBLISHER_TOPIC")
STATUS_TOPIC = str("STATUS_TOPIC")

##################################################
#MQTT CONSTANTS
##################################################
MQTT_BROKER_ADDRESS = "0.0.0.0" 
MQTT_BROKER_PORT = 1883
# MQTT_BROKER_ADDRESS = "52.77.234.153"
# MQTT_BROKER_PORT = 30006
MQTT_USER = "guest"
MQTT_PASSWORD = "guest"

MQTT_NAVIGATION_TOPIC = "nus5gdt/robots/mindpointeye/navigate"
MQTT_MARKER_TOPIC = "nus5gdt/robots/mindpointeye/marker"
MQTT_ROBOT_STATE_TOPIC = "nus5gdt/robots/mindpointeye/robot_state"



#MQTT address and port
mqtt_broker_address = None
mqtt_broker_port = None
#username and password
mqtt_user = None
mqtt_password = None
#RabbitMQ topics
task_publisher_topic =  None
status_topic = None
#Digital Twin topics
mqtt_navigation_topic = None
mqtt_marker_topic = None
mqtt_robot_state_topic = None
#RabbitMQ address
aio_rabbitmq_url = None
mqtt_rabbitmq_url = None


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
    mqtt_broker_address = MQTT_BROKER_ADDRESS
    mqtt_broker_port = MQTT_BROKER_PORT

    #username and password
    mqtt_user = MQTT_USER
    mqtt_password = MQTT_PASSWORD

    #RabbitMQ topics
    task_publisher_topic = TASK_PUBLISHER_TOPIC
    status_topic = STATUS_TOPIC

    #Digital Twin topics
    mqtt_navigation_topic = MQTT_NAVIGATION_TOPIC
    mqtt_marker_topic = MQTT_MARKER_TOPIC
    mqtt_robot_state_topic = MQTT_ROBOT_STATE_TOPIC

    #RabbitMQ address
    aio_rabbitmq_url = AIO_RABBITMQ_URL
    mqtt_rabbitmq_url = MQTT_RABBITMQ_URL


    #MQTT address and port
    if args.mqtt_broker_address:
        mqtt_broker_address = args.mqtt_broker_address
    if args.mqtt_broker_port:
        mqtt_broker_port = args.mqtt_broker_port

    #username and password
    if args.mqtt_user:
        mqtt_user = args.mqtt_user
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



if __name__ == "__main__":
    parse_arguments()