# Seccion de importe de librerias
# Librerias de manejo de ros2
import roslibpy
# Librerias de adquisicion de argumentos de entrada
import argparse
# Librerias para manejo de archivos
from glob import glob
import json
from time import time, sleep
# Importe de librerias propias
# Libreria de acceso a funcionalidades de gtp
from prompt import OpenAIInterface, append_service, check_type, use_action
from utils.record_functions import SpeechToText
from utils.data_important import RECORDING_PATH, API_DEEP
from utils.deep_owm import DeepGrammClass

# Deteccion de argumentos de entrada
def args_factory() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", type=str, required=True, help="OpenAI API key.")
    parser.add_argument(
        "--api", type=str, default="turtlesim_msgs/srv", help="Path to API JSON file."
    )
    #parser.add_argument("--host", type=str, default="localhost", help="ROS host.")
    parser.add_argument("--host", type=str, default='192.168.12.169', help="ROS host.")
    parser.add_argument("--port", type=int, default=9090, help="ROS port.")
    parser.add_argument(
        "--model", type=str, default="gpt-4o-mini", help="OpenAI model."
    )
    args = parser.parse_args()
    return args

# Funcion de ejecucion general 
def main() -> None:
    # Carga de argumentos de entrada
    args = args_factory()

    # Carga de funciones propias para ejecucion de acciones en robot
    api = []
    for api_file in glob(f"{args.api}/*.json"):
        with open(api_file, "r") as f:
            api.append(json.load(f))

    # Carga de objetos e interfaz de comunicacion
    new_obj = SpeechToText()
    new_deep = DeepGrammClass(API_DEEP)
    # Creacion de objeto de interfaz de comunicacion con gtp
    interface = OpenAIInterface(api=api, key=args.key)

    # Creacion de cliente de ros, comunicacion con puerto especifico
    ros_client = roslibpy.Ros(host=args.host, port=args.port)
    ros_client.run()
    
    # Lista de servicios
    services = {}

    # Ciclo de ejecucion de solicitudes
    while True:
        try:
            # Creacion de nueva solicitud
            # Entrada de texto de solicitud de usuario
            prompt = input("Would you like to place a new order? y/n")

            # Validacion de nueva solicitud
            if prompt == "n":
                print("Request completed.")
                break

            print("Please describe the command you want to execute on the robot. The recording will automatically stop when you finish speaking.")

            # pausa para deteccion de audio
            sleep(1)

            # Seccion de escucha de solicitud
            print("Listening...")
            new_obj.getSpeech()
            print("End listen")

            # Inicio de ejecucion de transcripcion
            current_time = time()
            # Inicio de ejecucion asincrona
            words = new_deep.trascription(RECORDING_PATH)
            print(f"Orden solicitada: {words}")
            # Tiempo de transcripcion general
            general_time = time() - current_time

            print(f"Time of execution: {general_time}")

            # Inicio de solicitud en gtp
            # Validacion de estado de comunicacion
            print("Generating API calls. This may take some time...")
            # Envio de solicitud, y recibimiento de respuesta de api
            generated_api_calls = interface.prompt_to_api_calls(
                words, model=args.model
            )
            # Validacion de respuesta
            print("Done.")

            # Ciclo para lectura de respuestas de la api
            for call in generated_api_calls:
                # validacion de lectura
                
                #List args from call
                list_temp = list(call.keys())
                # Variable to id fucntion
                id_function = check_type(
                    list_temp
                )

                if id_function == 0:
                    print("Getting required service. This might take some time...")
                    services = append_service(ros_client, call["service"], services)
                    print("Done.")

                if id_function == 1:
                    print("Getting required action. This might take some time...")
                    print(call["args"]["pose"]["position"])
                    if use_action(
                        ros_client, 
                        call["action"],
                        call
                    ):
                        print("action completado correctamente")
                    continue
                
                if id_function < 0:
                    print("Can't recognize the function")
                    continue

                try:
                    print(
                        "Calling service {} with args {}".format(
                            call["service"], call["args"]
                        )
                    )
                    input("Press Enter to continue...")
                    service = services[call["service"]]
                    request = roslibpy.ServiceRequest(call["args"])
                    service.call(request)
                except Exception as e:
                    print(f"Failed to call service with {e}.")

        except KeyboardInterrupt:
            break

    ros_client.terminate()


if __name__ == "__main__":
    main()