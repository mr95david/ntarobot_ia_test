# Seccion de importe de librerias
# Librerias utilitarias y busqueda de archivos y ubicaciones
import argparse
import json
from glob import glob
# Libreria de interaccion con ros
import roslibpy
# Importe de libreiras propias
from prompt import OpenAIInterface, append_service, check_type, use_action

# Deteccion de valores de argumentos de entrada, para ejecucion de codigo general
def args_factory() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", type=str, required=True, help="OpenAI API key.")
    parser.add_argument(
        "--api", type=str, default="turtlesim_msgs/srv", help="Path to API JSON file."
    )
    parser.add_argument("--host", type=str, default="localhost", help="ROS host.")
    parser.add_argument("--port", type=int, default=9090, help="ROS port.")
    parser.add_argument(
        "--model", type=str, default="gpt-4o-mini", help="OpenAI model."
    )
    args = parser.parse_args()
    return args

# Funcion de ejecucion de main del funcionamiento general de la coumnicacion con la api
def main() -> None:
    # Declaracion e inicializacion de argumentos de entrada especificos
    args = args_factory()

    # Creaccion de lista de ordenes para ejecuccion de acciones sobre el robot
    api = []
    for api_file in glob(f"{args.api}/*.json"):
        with open(api_file, "r") as f:
            api.append(json.load(f))

    # Asignacion e inicializacion de objeto, para interpretacion bi-modal con el modelo de ia
    interface = OpenAIInterface(api=api, key=args.key)

    # Creacion de cliente de ros, comunicacion con puerto especifico
    ros_client = roslibpy.Ros(host=args.host, port=args.port)
    ros_client.run()

    # Lista de servicios
    services = {}
    # Lista de acciones (prueba de identificacion de tipo de ejecucion) - nuevo
    actions = {}

    # Ciclo continuo de ejecucion de comunicacion con la api
    while True:
        try:
            # Entrada de texto de solicitud de usuario
            prompt = input("Enter a prompt: ")
          
            # Validacion de estado de comunicacion
            print("Generating API calls. This may take some time...")
            # Envio de solicitud, y recibimiento de respuesta de api
            generated_api_calls = interface.prompt_to_api_calls(
                prompt, model=args.model
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
