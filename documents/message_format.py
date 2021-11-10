1.1 Move to marker point
"""
JSON:
    {
        # User-defined params
        "uuid": 'ROBOT01_UUID0001',
        "args": '{"target_marker": "pointA"}' ,

        # Default params
        "type": 0,              #Task type "action"
        "level: 3,              #Task priority          "IMPORTANT"
        "exec_type": 2,         #Type of task execute   "immediate_exec"
        "source": 0,            #Task creator
        "action": 2,            #Task execute API.      "move_single"
        "require_return": True,
    }

Protobuf:

    robot_message = robotTask_pb2.RequestMessage()
    robot_task = robot_message.robotTask.add()

    # User-defined params
    robot_task.uuid = 'ROBOT01_UUID0001'
    robot_task.args = '{"target_marker": "ChargeStation"}'

    # Default params
    robot_task.type = 0
    robot_task.level = 3
    robot_task.exec_type = 2
    robot_task.source = 0
    robot_task.action = 2
    robot_task.args = '{"target_marker": "ChargeStation"}'
    robot_task.require_return = True


"""


2. Cancellation of movement function
"""
JSON:
    {
        # User-defined params
        "uuid": 'ROBOT01_UUID0001',
        "args": '{"cancel_uuid": "ROBOT01_UUID0001"}' ,

        # Default params
        "type": 1,              #Task type              "order"
        "level: 3,              #Task priority          "IMPORTANT"
        "exec_type": 2,         #Type of task execute   "immediate_exec"
        "source": 0,            #Task creator
        "order": 0,            
        "require_return": True,
    }

Protobuf:

    robot_message = robotTask_pb2.RequestMessage()
    robot_task = robot_message.robotTask.add()

    # User-defined params
    robot_task.uuid = 'ROBOT01_UUID0001_'
    robot_task.args = '{"cancel_uuid": "ROBOT01_UUID0001"}'

    # Default params
    robot_task.type = 1
    robot_task.level = 3
    robot_task.exec_type = 2
    robot_task.source = 0
    robot_task.order = 0
    robot_task.require_return = True

"""


3.1 Marker Point Creation
"""
JSON:
    {
        # User-defined params
        "uuid": 'ROBOT01_UUID0001',
        "args": '{"marker_name": "pointA", "x": 0.0, "y": 0.0, "theta": 0.0}' ,

        # User-defined params
        "type": 1,              #Task type              "order"
        "level: 3,              #Task priority          "IMPORTANT"
        "exec_type": 2,         #Type of task execution  "immediate_exec"
        "source": 0,            #Task creator           "server"
        "order": 8              #Order
        "require_return": True
    }

Protobuf:

    robot_message = robotTask_pb2.RequestMessage()
    robot_task = robot_message.robotTask.add()

    # User-defined params
    robot_task.uuid = 'ROBOT01_UUID0001'
    robot_task.args = '{"marker_name": "pointA", "x": 0.0, "y": 0.0, "theta": 0.0}'

    # Default params
    robot_task.type = 1
    robot_task.level = 3
    robot_task.exec_type = 2
    robot_task.source = 0
    robot_task.order = 8
    robot_task.require_return = True
"""

3.2 Marker Point Deletion
"""
JSON:
    {
        # User-defined params
        "uuid": 'ROBOT01_UUID0001',
        "args": '{"marker_name": "pointA"}' ,

        # Default params
        "type": 1,              #Task type              "order"
        "level: 3,              #Task priority          "IMPORTANT"
        "exec_type": 2,         #Type of task execution  "immediate_exec"
        "source": 0,            #Task creator           "server"
        "order": 9              #Order
        "require_return": True
    }

Protobuf:

    robot_message = robotTask_pb2.RequestMessage()
    robot_task = robot_message.robotTask.add()

    # User-defined params
    robot_task.uuid = 'ROBOT01_UUID0001'
    robot_task.args = '{"marker_name": "ChargeStation"}'

    # Default params
    robot_task.type = 1
    robot_task.level = 3
    robot_task.exec_type = 2
    robot_task.source = 0
    robot_task.order = 9
    robot_task.require_return = True
"""