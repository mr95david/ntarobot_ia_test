# Importe de librerias
# Librerias de procesamiento
import rhasspysilence
import pyaudio
# Librerias utilitarias
import io # Interfaces and handling
from typing import Optional
import time
import wave
from pathlib import Path
import os
# Librerias propias
from .data_important import PATH_AUDIO

# Clase para obtencion de audio
class SpeechToText:
    # Constructor de clase 
    def __init__(self) -> None:
        
        # variable de instancia para recibir un audio
        self.pa_ = pyaudio.PyAudio()

    # Funcion para reconocer el audio de un puerto especifico
    def getSpeech(self) -> None:
        
        # Funcion para obtener sonido
        recorder = rhasspysilence.WebRtcVadRecorder(
            vad_mode = 3,
            silence_seconds = 4
        )

        # Inicio de record
        recorder.start()

        # Directorio de almacenamiento
        # Validacion de existencia de existencia de directorio
        if not os.path.isdir(PATH_AUDIO):
            raise ValueError(f"Error, la ruta '{PATH_AUDIO}' no corresponde a un directorio!")
        
        wav_sink = PATH_AUDIO
        # Nombre de archivo almacenado de grabacion
        wav_filename = "recording"

        wav_sink_path = Path(wav_sink)

        wav_dir = wav_sink_path

        # Lectura de archivo ruta de directorio
        voice_command: Optional[rhasspysilence.VoiceCommand] = None

        # fuente de audio
        audio_source = self.pa_.open(
            rate = 16000,
            format=pyaudio.paInt16,
            channels=1,
            input=True,
            frames_per_buffer=960
        )

        audio_source.start_stream()

        try:
            chunk = audio_source.read(960)
            while chunk:
                # Look for speech/silence
                voice_command = recorder.process_chunk(chunk)

                if voice_command:
                    _ = voice_command.result == rhasspysilence.VoiceCommandResult.FAILURE
                    # Reset
                    audio_data = recorder.stop()
                    if wav_dir:
                        # Write WAV to directory
                        wav_path = (wav_dir / time.strftime(wav_filename)).with_suffix(
                            ".wav"
                        )
                        wav_bytes = self.buffer_to_wav(audio_data)
                        wav_path.write_bytes(wav_bytes)
                        break
                # Next audio chunk
                chunk = audio_source.read(960)

        finally:
            try:
                audio_source.close_stream()
            except Exception:
                pass
    
    def buffer_to_wav(self, buffer: bytes) -> bytes:
        """Wraps a buffer of raw audio data in a WAV"""
        rate = int(16000)
        width = int(2)
        channels = int(1)

        with io.BytesIO() as wav_buffer:
            wav_file: wave.Wave_write = wave.open(wav_buffer, mode="wb")
            with wav_file:
                wav_file.setframerate(rate)
                wav_file.setsampwidth(width)
                wav_file.setnchannels(channels)
                wav_file.writeframesraw(buffer)

            return wav_buffer.getvalue()

