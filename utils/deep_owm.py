# Seccion de importe de librerias
# Importe de libreria de deepgram
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
# Librerias de verificacion de tipo de datos
from typing import Any, Dict, List, Union
from os import PathLike

# Creacion de clase de bot para transformacion de voz en texto
class DeepGrammClass:
    # Constructor
    def __init__(
            self,
            api_key: str # Valor de key requerida para conexion con API
        ) -> None:
        
        # Inicializacion de variables de instancia
        self.client_ = DeepgramClient(api_key)
        # Configuracion de opciones de deep
        self.options_ = PrerecordedOptions(
            model = "nova-2",
            smart_format = True
        )

    # Funcion de solicitud de transcripcion
    def trascription(
            self,
            file_name: Union[Union[str, bytes, PathLike[str], PathLike[bytes]], int]
        ):
        
        # Ejecucion de lectura de audio recibido y procesamiento
        with open(file_name,"rb") as audio:
            # Fuente de audio recibido
            source: FileSource = {"buffer": audio, "mimetype": "audio/wav"}
            # Solicitud de transcripcion a cliente de deepgram
            response = self.client_.listen.prerecorded.v("1").transcribe_file(source, self.options_)
            #transcribe_file(source, self.options_)

            return response.results["channels"][0]["alternatives"][0]["transcript"]