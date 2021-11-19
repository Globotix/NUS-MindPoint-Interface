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

#Install python installer to package python programs as standalone executables
pip install pyinstaller
```

# Quick Start

1. Compile protobuf messages
```
protoc -I=$SRC_DIR --python_out=$DST_DIR $SRC_DIR/addressbook.proto
```

2. Compile python executable for distribution (Only on the same CPU architecture (ARM/ x86))
```
pyinstaller --onefile main.py
```

3. Compile Python bytecode .pyc
```
python3 -m compileall -b .
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

- If need be, Modify rabbimq config file ("/etc/rabbitmq/rabbitmq.conf")
```
mqtt.listeners.tcp.default = 1883
## Default MQTT with TLS port is 8883
# mqtt.listeners.ssl.default = 8883

# anonymous connections, if allowed, will use the default
# credentials specified here
mqtt.allow_anonymous  = true
mqtt.default_user     = guest
mqtt.default_pass     = guest

#every connection belongs to a virtual host. Some messaging protocols have the concept of vhosts, others don't. MQTT falls into the latter category. Therefore the MQTT plugin needs to provide a way to map connections to vhosts.
mqtt.vhost            = /
mqtt.exchange         = amq.topic

# 24 hours by default
mqtt.subscription_ttl = 86400000
mqtt.prefetch         = 10

```

## Errors

1. Durable queues
```
PRECONDITION_FAILED - inequivalent arg 'durable' for queue 'STATUS_TOPIC' in vhost '/': received 'false' but current is 'true'
```
Make sure that the durable fields in publisher and subscriber are set to the same boolean value. And then run the following cmd and try again:
```
rabbitmqadmin delete queue name=name_of_queue
```