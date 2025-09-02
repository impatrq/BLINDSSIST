import cv2
import pyttsx3
import subprocess
import numpy as np
import signal
import sys
import os # Para verificar la existencia del modelo YOLO

# Importar YOLO 
from ultralytics import YOLO

"""Clase camara"""

class Camara:
    
    """Captura de frames"""
    def __init__(self, voz_manager, width=640, height=480):
        self.__voz = voz_manager
        self.__width = width
        self.__height = height

    def capturar_frame(self):
        """Captura con libcam conversion a array para openCV"""
        try:
            command = [
                'libcamera-still', '-t', '1',
                '--width', str(self.__width), '--height', str(self.__height),
                '-o', '-', '--denoise', 'off', '--nopreview'
            ]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            image_bytes, err = process.communicate()
            
            if process.returncode != 0:
                error_msg = f"libcamera-still falló. Código de error: {process.returncode}."
                self.__voz.hablar(error_msg)
                return None

            image_array = np.frombuffer(image_bytes, dtype=np.uint8)
            frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            if frame is None:
                error_msg = "No se pudo decodificar la imagen de la cámara."
                self.__voz.hablar(error_msg)
            
            return frame

        except FileNotFoundError:
            error_msg = "El comando 'libcamera-still' no se encontró."
            self.__voz.hablar(error_msg)
            sys.exit(1)
        except Exception as e:
            error_msg = f"Fallo al capturar el frame."
            self.__voz.hablar(error_msg)
            return None