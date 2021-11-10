import paho.mqtt.client as mqtt #import the client1
import time
import json

##############################################
#Broker attributes
##############################################
broker_address = "0.0.0.0" 
broker_port = 1883
mqtt_user = "guest"
mqtt_password = "guest"

mqtt_topic = "test_topic"

##############################################
#Callbacks
##############################################
def on_connect(client, userdata, flags, rc):
    if rc == 0: 
          print("Connected to MQTT broker (RC: %s)" % rc)
    else:
          print("Connection to MQTT broker failed (RC: %s)" % rc)
def on_log(client, userdata, level, buf):
    print(buf)
def on_publish(client, userdata, mid):
    print("Data published (Mid: %s)" % mid)
def on_disconnect(client, userdata, rc):
    if rc != 0:
          print("Unexpected disconnect")
    print("Disconnected from MQTT broker")

#Connect to MQTT Broker
client = mqtt.Client("mqtt_test") #create new instance

#[Optional] Set username and password
client.username_pw_set(mqtt_user, mqtt_password)

client.connect(broker_address, broker_port, 60) #connect to broker

#Register callbacks
client.on_connect = on_connect
client.on_log = on_log
client.on_publish = on_publish
client.on_disconnnect = on_disconnect

while True:
    _data = {}
    _data["boy"] = str("oh boy")
    _data_json = json.dumps(_data)
    client.publish(mqtt_topic, _data_json, 1) #wtf is the last number
    time.sleep(1)
client.loop_stop()
client.disconnect()
