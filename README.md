# NUS Mindpoint Intermediary Node

The objective of this node is to act as an intermediary layer between the Mindpoint API and NUS Digital Twin MQTT interface.
This node should convert MQTT messages from the NUS Digital Twin model to Protobuf messages for the Mindpoint API and vice versa.

# Dependencies to be installed

1. RabbitMQ
```
```

2. paho-mqtt
```
pip install paho-mqtt
```
3. Mosquitto - MQTT Broker
```
snap install mosquitto
sudo apt-get install mosquitto
sudo apt-get install mosquitto-clients
```

4. aio_pika

5. asyncio

# Pre-requisite steps

1. First enable MQTT support in RabbitMQ by enabling a MQTT adapter plugin (already installed with standard shipment of RabbitMQ)
```
rabbitmq-plugins enable rabbitmq_mqtt
```

2. Enable rabbitmq dashboard and access management dashboard
```
rabbitmq-plugins enable rabbitmq_management
```
Then access
```
http://0.0.0.0:15672/
```

3. Create new user for MQTT connections with full access to default virtual host
```
# username and password are both "mqtt-test"
rabbitmqctl add_user mqtt-test mqtt-test
rabbitmqctl set_permissions -p / mqtt-test ".*" ".*" ".*"
rabbitmqctl set_user_tags mqtt-test management
```

4. Modify rabbimq config file ("/etc/rabbitmq/rabbitmq.conf")
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

# Quick Start
1. First figure out how to use MQTT - Done

2. Next try to use MQTT plugin with RabbitMQ

3. Figure out how to send protobuf over RabbitMQ

# Broker Guide
## Mosquitto

- Start and stop service
```
sudo service  mosquitto stop
sudo service mosquitto start #see note later
```
- The stop/start scripts start the mosquitto broker in the background and also use the default mosquitto.conf file in the /etc/mosquitto/ folder.

- Test subscribe
mosquitto_sub -v -h localhost -t \# -d

## RabbitMQ 

- List queus
```
sudo rabbitmqctl list_queues
```

- 

# Open Issues

1. What is "order"? As in "robot_task.order = 8" in "3.1 Create marker point at specific coordinates"

2. Is theta in radians/degrees

3.


# Already implemented

- NUS Digital Twin takes in MQTT
- Max uses paho-mqtt to send MQTT message and Mosquitto as a broker service


# References
- rabbitmq.com/mqtt.html
- https://blogs.sap.com/2016/02/21/uniting-amqp-and-mqtt-message-brokering-with-rabbitmq/
- http://wiki.ros.org/mqtt_bridge
- http://www.steves-internet-guide.com/install-mosquitto-linux/