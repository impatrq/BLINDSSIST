import pyttsx3 
import subprocess 
import numpy as np 
import signal 
import sys 
import os 
import cv2
from ultralytics import YOLO 
import time 

class Camara:
    
    """Captura de imagenes"""
    def __init__(self, voz_manager, width=640, height=480):
        self.__voz = voz_manager
        self.__width = width
        self.__height = height

    def capturar_frame(self):
        
        """Captura con libcamera y arrays para OpenCv"""
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

class Voz:
    
    """Maneja sintesis de voz"""
    def __init__(self):
        self.__engine = None
        try:
            self.__engine = pyttsx3.init()
            self.__engine.setProperty('rate', 150)
            self._set_spanish_voice()
        except Exception as e:
            sys.exit(1)

    def _set_spanish_voice(self):
        if self.__engine is None: return
        voices = self.__engine.getProperty('voices')
        for voice in voices:
            if 'es' in voice.languages or 'spanish' in voice.name.lower():
                self.__engine.setProperty('voice', voice.id)
                return

    def hablar(self, texto):
        
        """pronuncia texto dado"""
        if self.__engine is not None:
            self.__engine.say(texto)
            self.__engine.runAndWait()
        
    def detener(self):
        
        """detiene motor de voz"""
        if self.__engine is not None:
            self.__engine.stop()

class Traductor:
    
    """gestiona el diccionario"""
    def __init__(self):
        
        self.__traducciones = {
            'person': 'persona',
            'car': 'auto',
            'bicycle': 'bicicleta',
            'motorcycle': 'moto',
            'bus': 'colectivo',
            'truck': 'camión',
            'cell phone': 'celular',
            'bottle': 'botella',
            'tv': 'televisor'
        }

    def traducir(self, palabra_ingles):
        return self.__traducciones.get(palabra_ingles, palabra_ingles)
        
    def obtener_clases_permitidas(self):
        return list(self.__traducciones.keys())

class IA:
    
    """analiza la imagen con YOLO"""
    def __init__(self, voz_manager, model_path="yolov8n.pt", confidence_threshold=0.6, allowed_classes=None):
        self.__voz = voz_manager
        if not os.path.exists(model_path):
            error_msg = "El archivo del modelo de inteligencia artificial no se encontró."
            self.__voz.hablar(error_msg)
            sys.exit(1)
        try:
            self.__model = YOLO(model_path)
            self.__confidence_threshold = confidence_threshold
            self.__allowed_classes = allowed_classes if allowed_classes else []
        except Exception as e:
            error_msg = "No se pudo cargar el modelo de inteligencia artificial."
            self.__voz.hablar(error_msg)
            sys.exit(1)
            
    def analizar_imagen(self, frame):
        results = self.__model(frame, verbose=False)[0]
        objetos_detectados = {}
        for box in results.boxes:
            class_id = int(box.cls[0])
            class_name = self.__model.names[class_id]
            confidence = float(box.conf[0])

            if class_name in self.__allowed_classes and confidence > self.__confidence_threshold:
                objetos_detectados[class_name] = objetos_detectados.get(class_name, 0) + 1
        return objetos_detectados

class Main:
    
    """clase principal maneja lsa demas clases"""
    def __init__(self):
        self.__voz = Voz()
        self.__traductor = Traductor()
        self.__camara = Camara(voz_manager=self.__voz)
        self.__ia = IA(
            voz_manager=self.__voz,
            model_path="yolov8n.pt", 
            confidence_threshold=0.6, 
            allowed_classes=self.__traductor.obtener_clases_permitidas()
        )
        self.__last_detected_objects = {}

    def __anunciar_detecciones(self, objetos_actuales):
        
        """compara las detecciones y anuncia l"""
        anuncios = []
        
        for class_name, count in objetos_actuales.items():
            last_count = self.__last_detected_objects.get(class_name, 0)
            if count != last_count:
                spanish_name = self.__traductor.traducir(class_name)
                
                if count == 1:
                    message = f"Una {spanish_name} detectada."
                else:
                    message = f"{count} {spanish_name}s detectados."
                anuncios.append(message)
        
        for class_name, last_count in self.__last_detected_objects.items():
            if class_name not in objetos_actuales and last_count > 0:
                spanish_name = self.__traductor.traducir(class_name)
                message = f"Ya no hay {spanish_name}s."
                anuncios.append(message)

        if anuncios:
            final_message = ", ".join(anuncios)
            self.__voz.hablar(final_message)
            
        self.__last_detected_objects = objetos_actuales.copy()

    def iniciar(self):
        self.__voz.hablar("Iniciando detección de objetos. Presiona control c para salir.")
        
        while True:
            frame = self.__camara.capturar_frame()
            if frame is None:
                time.sleep(1)
                continue
            
            objetos_actuales = self.__ia.analizar_imagen(frame)
            self.__anunciar_detecciones(objetos_actuales)
            
            time.sleep(0.5)

def main():
    asistente = Main()

    def exit_handler(sig, frame):
        asistente._Main__voz.detener() 
        sys.exit(0)
    
    signal.signal(signal.SIGINT, exit_handler)
    
    asistente.iniciar()

if __name__ == "__main__":
    main()