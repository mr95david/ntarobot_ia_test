# # Importe de librerias
# import roslibpy
# import json

# import roslibpy.actionlib

# def main():
#     pass

# if __name__ == "__main__":
#     ros_client = roslibpy.Ros(host="localhost", port=9090)
#     ros_client.run()
#     new_action = roslibpy.actionlib.ActionClient(
#         ros_client,
#         "/new_action",
#         "action"
#     )



#     ros_client.terminate()



import roslibpy
import roslibpy.actionlib

client = roslibpy.Ros(host='localhost', port=9090)
server = roslibpy.actionlib.SimpleActionServer(client, '/fibonacci', 'actionlib_tutorials/FibonacciAction')

def execute(goal):
    print('Received new fibonacci goal: {}'.format(goal['order']))

    seq = [0, 1]

    for i in range(1, goal['order']):
        if server.is_preempt_requested():
            server.set_preempted()
            return

        seq.append(seq[i] + seq[i - 1])
        server.send_feedback({'sequence': seq})

    server.set_succeeded({'sequence': seq})


server.start(execute)
client.run_forever()

