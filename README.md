# NUS Mindpoint Intermediary Node

The objective of this node is to act as an intermediary layer between the Mindpoint API and NUS Digital Twin MQTT interface.
This node should convert MQTT messages from the NUS Digital Twin model to Protobuf messages for the Mindpoint API and vice versa.

# Dependencies to be installed

RabbitMQ: Refer to https://www.rabbitmq.com/download.html


#Install the following python packages
```
# paho-mqtt
pip install paho-mqtt

# Mosquitto - MQTT Broker
snap install mosquitto
sudo apt-get install mosquitto
sudo apt-get install mosquitto-clients

# aio_pika
pip install aio-pika

# asyncio
pip install asyncio

# protobuf
pip install protobuf
```

# Quick Start

1. Compile protobuf messages
```
protoc -I=$SRC_DIR --python_out=$DST_DIR $SRC_DIR/addressbook.proto
```


# Broker Guide
## Mosquitto

- Start and stop service
```
sudo service mosquitto stop
sudo service mosquitto start #see note later
```

- The stop/start scripts start the mosquitto broker in the background and also use the default mosquitto.conf file in the /etc/mosquitto/ folder.

- Subscribe to all topics
```
mosquitto_sub -v -h localhost -t \# -u guest -P guest -d
```

- Publish on topic "mp/navigate"
```
mosquitto_pub -h localhost -t mp/navigate -u guest -P guest -m {\"hey\":\"HO\"} 
```

## RabbitMQ 

- List queus
```
sudo rabbitmqctl list_queues
```

