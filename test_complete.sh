#!/bin/bash

#var for session name
sn=remote_management_node

#start session
tmux new-session -s "$sn" -n etc -d 

tmux split-window -dh $TMUX_PANE
tmux split-window -v $TMUX_PANE
tmux split-window -v -t 0.2 $TMUX_PANE
tmux split-window -v -t 0.3 $TMUX_PANE

#Launch main node
tmux send-keys -t 0.0 "./main" C-m

#MQTT TEST 1: MQTT Subscription to check robot status
tmux send-keys -t 0.1 "mosquitto_sub -v -h localhost -t \# -u guest -P guest -d" C-m

#MQTT TEST 2: MQTT publishing to check sending robot task
# tmux send-keys -t 0.2 "mosquitto_pub -h localhost -t "nus5gdt/robots/mindpointeye/navigate" -u guest -P guest -m "{\"uuid\":\"ROBOT01_UUID0001\", \"action\":\"start_movement\", \"target_marker\":\"pointA\" }"" 
# mosquitto_pub -h localhost -t "nus5gdt/robots/mindpointeye/navigate" -u guest -P guest -m "{\"uuid\":\"ROBOT01_UUID0001\", \"action\":\"start_movement\", \"target_marker\":\"pointA\" }"
# mosquitto_pub -h localhost -t "nus5gdt/robots/mindpointeye/marker" -u guest -P guest -m "{\"uuid\":\"ROBOT01_UUID0001\", \"action\":\"create_marker\", \"marker_name\":\"pointA\", \"pos_x\":1.0, \"pos_y\": 2.0, \"pos_theta\": 3.0}"


#RabbitMQ Test 1: Launch RabbitMQ subscription to TASK_PUBLISHER_TOPIC
tmux send-keys -t 0.3 "python3 test/test_pub_rabbitmq_status_topic.py" C-m

#RabbitMQ Test 2: Launch RabbitMQ Publishing of robot state to STATUS_TOPIC
tmux send-keys -t 0.4 "python3 test/test_sub_rabbitmq_task_publisher_topic.py" C-m


tmux -2 attach-session -d
