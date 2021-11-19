
"""
Test RabbitMQ publishing to STATUS_TOPIC 
"""

#!/usr/bin/env python
import pika, sys, os
import time

import json

PUBLISH_FREQUENCY = 2

TASK_PUBLISHER_TOPIC = str("TASK_PUBLISHER_TOPIC")
STATUS_TOPIC = str("STATUS_TOPIC")

def test_fake_status_msg():
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

class AMQPPublisher():
    def __init__(self, hostname):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=str(hostname)))
        self.channel = self.connection.channel()
        
        #Creates a queue, makes sure that it exists
        self.channel.queue_declare(queue=STATUS_TOPIC, durable= True)

        while True:
            json_msg = test_fake_status_msg()
            self.channel.basic_publish(exchange='', routing_key=STATUS_TOPIC, body=test_fake_status_msg())
            print("RabbitMQ: Sent Status msg on " + STATUS_TOPIC,)
            time.sleep(PUBLISH_FREQUENCY)

def main():
    print("--------------------------")
    print("Started RabbitMQ Publisher for STATUS_TOPIC")
    print("--------------------------")

    amqp_publisher = AMQPPublisher('localhost')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)