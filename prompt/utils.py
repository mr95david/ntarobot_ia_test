from typing import Dict

import roslibpy
import roslibpy.actionlib
import time


def append_service(
    client: roslibpy.Ros, name: str, services: Dict[str, roslibpy.Service]
) -> Dict[str, roslibpy.Service]:
    """Update current services with the required one.

    Args:
        client (roslibpy.Ros): ROS client.
        name (str): Required service name.
        services (Dict[str, roslibpy.Service]): Dictionary of current services.

    Returns:
        Dicr[str, roslibpy.Service]: Updated dictionary of services.
    """
    if name not in services:
        services[name] = roslibpy.Service(client, name, client.get_service_type(name))
    return services

# Function for append action
def use_action(
    client: roslibpy.Ros, name: str, values: Dict
) -> bool:
    # Definition of action client
    action_client = roslibpy.actionlib.ActionClient(
        client, # Cliente de ejecucion de ros
        server_name = name,
        action_name ='nav2_msgs/action/NavigateToPose'
    )

    # Goal objective
    goal = {
        'pose': {
            'header': {
                'frame_id': 'map',
                'stamp': {
                    'secs': int(time.time()),
                    'nsecs': int((time.time() % 1) * 1e9)
                }
            },
            'pose': {
                'position': {
                    'x': values["args"]["pose"]["position"]['x'],
                    'y': values["args"]["pose"]["position"]['y'],
                    'z': 0.0
                },
                'orientation': {
                    'x': 0.0,
                    'y': 0.0,
                    'z': values["args"]["pose"]["orientation"]['z'],
                    'w': values["args"]["pose"]["orientation"]['w']
                }
            }
        }
    }

    action_client.send_goal(goal)

    while True:
        result = action_client.get_result()
        if result:
            print('Result:', result)
            break
        time.sleep(1)
    
    return True



# Function for identify if is action or server
def check_type(args_list: list) -> int:
    # Validation 
    if "service" in args_list:
        return 0
    
    if "action" in args_list:
        return 1
    
    return -1