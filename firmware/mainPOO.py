# main.py
from picamera2 import Picamera2
from ultralytics import YOLO
import cv2
import subprocess
import signal
import sys
import os
import time

# --- Módulos del Proyecto (Clases) ---

class Camara:
    """Controla la captura de frames de la cámara de la Raspberry Pi."""
    def __init__(self, width=640, height=480):
        self.__width = width
        self.__height = height
        self.__picam2 = None
        print("[INFO] Módulo de Cámara inicializado.")

    def iniciar(self):
        """Inicia el stream de la cámara."""
        try:
            self.__picam2 = Picamera2()
            config = self.__picam2.create_preview_configuration(main={"size": (self.__width, self.__height)})
            self.__picam2.configure(config)
            self.__picam2.start()
            print("[INFO] Cámara iniciada. Stream en vivo.")
            return True
        except Exception as e:
            print(f"[ERROR] No se pudo iniciar la cámara: {e}")
            return False

    def detener(self):
        """Detiene el stream de la cámara."""
        if self.__picam2:
            self.__picam2.stop()
            print("[INFO] Cámara detenida.")

    def capturar_frame(self):
        """Captura un solo frame del stream y lo devuelve como un array de OpenCV."""
        if self.__picam2:
            frame = self.__picam2.capture_array()
            return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return None

class Voz:
    """Maneja la síntesis de voz a través de espeak."""
    def __init__(self):
        print("[INFO] Módulo de Voz inicializado.")

    def hablar(self, texto):
        """Pronuncia el texto dado usando subprocess y espeak."""
        try:
            subprocess.run(['espeak', f'"{texto}"'], check=True)
        except Exception as e:
            print(f"[ERROR] Fallo al reproducir audio con espeak: {e}")

class Traductor:
    """Gestiona el diccionario de traducciones."""
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
        print("[INFO] Módulo de Traductor inicializado.")

    def traducir(self, palabra_ingles):
        """Traduce una palabra del inglés al español."""
        return self.__traducciones.get(palabra_ingles, palabra_ingles)
        
    def obtener_clases_permitidas(self):
        """Devuelve la lista de clases que el traductor conoce."""
        return list(self.__traducciones.keys())

class IA:
    """Analiza las imágenes usando el modelo YOLOv8."""
    def __init__(self, model_path, confidence_threshold, allowed_classes):
        if not os.path.exists(model_path):
            print(f"[ERROR] El archivo del modelo '{model_path}' no se encontró.")
            sys.exit(1)
        try:
            self.__model = YOLO(model_path)
            self.__confidence_threshold = confidence_threshold
            self.__allowed_classes = allowed_classes
            print(f"[INFO] Módulo de IA (YOLOv8) cargado desde '{model_path}'.")
        except Exception as e:
            print(f"[ERROR] No se pudo cargar el modelo YOLOv8: {e}")
            sys.exit(1)
            
    def analizar_imagen(self, frame):
        """Analiza un frame y devuelve un diccionario con los objetos detectados."""
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
    """Clase principal que orquesta el asistente visual."""
    def __init__(self):
        self.__traductor = Traductor()
        self.__voz = Voz()
        self.__camara = Camara()
        self.__ia = IA(
            model_path="yolov8n.pt", 
            confidence_threshold=0.6, 
            allowed_classes=self.__traductor.obtener_clases_permitidas()
        )
        self.__last_detected_objects = {}

    def __anunciar_detecciones(self, objetos_actuales):
        """Método privado para comparar detecciones y anunciar los cambios."""
        anuncios = []
        
        # Anunciar objetos nuevos o cambios en la cantidad
        for class_name, count in objetos_actuales.items():
            last_count = self.__last_detected_objects.get(class_name, 0)
            if count != last_count:
                spanish_name = self.__traductor.traducir(class_name)
                message = f"Una {spanish_name} detectada." if count == 1 else f"{count} {spanish_name}s detectados."
                anuncios.append(message)
        
        # Anunciar objetos que ya no están
        for class_name, last_count in self.__last_detected_objects.items():
            if class_name not in objetos_actuales and last_count > 0:
                spanish_name = self.__traductor.traducir(class_name)
                message = f"Ya no hay {spanish_name}s."
                anuncios.append(message)

        if anuncios:
            final_message = ", ".join(anuncios)
            print(f"[INFO] Anuncio: {final_message}")
            self.__voz.hablar(final_message)
            
        self.__last_detected_objects = objetos_actuales.copy()

    def iniciar(self):
        """Inicia el ciclo principal del asistente."""
        if not self.__camara.iniciar():
            print("[ERROR] No se pudo iniciar el asistente sin la cámara.")
            return

        self.__voz.hablar("Iniciando detección de objetos. Presiona control c para salir.")
        
        try:
            while True:
                frame = self.__camara.capturar_frame()
                if frame is None:
                    time.sleep(1)
                    continue
                
                objetos_actuales = self.__ia.analizar_imagen(frame)
                self.__anunciar_detecciones(objetos_actuales)
                
                time.sleep(0.1) # Pequeña pausa para evitar el 100% de uso de CPU

        except KeyboardInterrupt:
            print("\n[INFO] Señal de interrupción recibida. Terminando programa.")
        except Exception as e:
            print(f"[ERROR] Ocurrió un error inesperado: {e}")
            
        finally:
            self.__camara.detener()
            print("[INFO] Sistema de detección detenido.")

def main():
    """Función de inicio del programa."""
    asistente = Main()
    asistente.iniciar()

if __name__ == "__main__":
    main()
