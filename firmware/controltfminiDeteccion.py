# main_combinado.py
from picamera2 import Picamera2
from ultralytics import YOLO
import cv2
import subprocess
import sys
import os
import time
import threading
import RPi.GPIO as GPIO
# Importar módulos para el sensor de distancia y control de motores
try:
    from TFmini3 import distancias, getTFminiData_uart1, getTFminiData_uart2, getTFminiData_uart3
except ImportError:
    print("[ERROR] No se pudo importar TFmini3. Asegúrate de que el archivo exista y esté en el PATH.")
    # Crear un placeholder para distancias si falla la importación, para que el código compile
    distancias = {"uart1": 200, "uart2": 200, "uart3": 200}
    
# --- Configuración de Hardware (Motores y PWM) ---
MOTOR_PIN1 = 18    # PWM 1
MOTOR_PIN2 = 13    # PWM 2

GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTOR_PIN1, GPIO.OUT)
GPIO.setup(MOTOR_PIN2, GPIO.OUT)

# PWM iniciales: 100 Hz, duty cycle en 0%
pwm1 = GPIO.PWM(MOTOR_PIN1, 100)
pwm2 = GPIO.PWM(MOTOR_PIN2, 100)

pwm1.start(0)
pwm2.start(0)
print("[INFO] GPIO y PWM de motores inicializados.")

# ----------------- MÓDULOS DEL PROYECTO (Clases) -----------------

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
    
    def __init__(self, velocidad=115): # Establece la velocidad predeterminada (e.g., 130 wpm)
        self.__velocidad = velocidad
        print("[INFO] Módulo de Voz inicializado.")

    def hablar(self, texto):
        """Pronuncia el texto dado usando subprocess y espeak con la velocidad configurada."""
        try:
            # Línea 80 - Modificación aquí
            # Se añaden el argumento '-s' y el valor de la velocidad a la lista de comandos
            command = ['espeak', f'-s {self.__velocidad}', f'"{texto}"']
            
            # Usar un hilo para no bloquear el bucle principal mientras espeak habla
            threading.Thread(target=lambda: subprocess.run(command, check=True)).start()
            
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

# ----------------- FUNCIONES DE CONTROL DE MOTORES (Envoltura para hilos) -----------------

def control_motor_uart1():
    """Control del motor basado en la lectura UART1 (pin MOTOR_PIN1)"""
    while True:
        d = distancias.get("uart1")
        if d is not None and d >= 0: # Verificar distancia válida
            if d < 120:
                duty = min(100, (120 - d))
            else:
                duty = 0
            pwm1.ChangeDutyCycle(duty)
            # print(f"[CONTROL_UART1] Distancia: {d} cm | Duty PWM1: {duty}%") # Descomentar para debug
        time.sleep(0.1)

def control_motor_uart2():
    """Control del motor basado en la lectura UART2 (pin MOTOR_PIN2)"""
    while True:
        d = distancias.get("uart2")
        if d is not None and d >= 0: # Verificar distancia válida
            if d < 120:
                duty = min(100, (120 - d))
            else:
                duty = 0
            pwm2.ChangeDutyCycle(duty)
            # print(f"[CONTROL_UART2] Distancia: {d} cm | Duty PWM2: {duty}%") # Descomentar para debug
        time.sleep(0.1)

def control_motor_uart3():
    """PWM intercalado entre ambos motores si la distancia < 120 cm"""
    toggle = True
    while True:
        d = distancias.get("uart3")
        if d is not None and d >= 0: # Verificar distancia válida
            if d < 120:
                duty = min(100, (120 - d))
                if toggle:
                    pwm1.ChangeDutyCycle(duty)
                    pwm2.ChangeDutyCycle(0)
                else:
                    pwm1.ChangeDutyCycle(0)
                    pwm2.ChangeDutyCycle(duty)
                toggle = not toggle
                # print(f"[CONTROL_UART3] Distancia: {d} cm | PWM intercalado con duty {duty}") # Descomentar para debug
            else:
                # ambos motores inactivos si la distancia >= 120
                pwm1.ChangeDutyCycle(0)
                pwm2.ChangeDutyCycle(0)
        time.sleep(0.3)
        
# ----------------- CLASE PRINCIPAL COMBINADA -----------------

class AsistenteCombinado:
    """Clase principal que orquesta el asistente visual y el control háptico."""
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
        self.__hilos_activos = []

    def __iniciar_hilos_tfmini(self):
        """Inicia los hilos de lectura UART y control de motores."""
        try:
            # Hilos de lectura UART (asumiendo que están definidos en TFmini3.py)
            t1 = threading.Thread(target=getTFminiData_uart1, daemon=True)
            t2 = threading.Thread(target=getTFminiData_uart2, daemon=True)
            t3 = threading.Thread(target=getTFminiData_uart3, daemon=True)

            t1.start()
            t2.start()
            t3.start()

            self.__hilos_activos.extend([t1, t2, t3])
            
            # Hilos de control PWM
            c1 = threading.Thread(target=control_motor_uart1, daemon=True)
            c2 = threading.Thread(target=control_motor_uart2, daemon=True)
            c3 = threading.Thread(target=control_motor_uart3, daemon=True)

            c1.start()
            c2.start()
            c3.start()
            
            self.__hilos_activos.extend([c1, c2, c3])
            print("[INFO] Hilos de TFmini3 y control de motores iniciados.")

        except NameError as e:
            print(f"[ADVERTENCIA] No se pudieron iniciar los hilos de TFmini3 (posiblemente porque no se importó: {e}). Continuando sin control háptico.")


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
                message = f"El objeto {spanish_name} ha desaparecido." # Mensaje ligeramente modificado
                anuncios.append(message)

        if anuncios:
            final_message = " ".join(anuncios) # Usamos espacio en lugar de coma para voz
            print(f"[INFO] Anuncio: {final_message}")
            self.__voz.hablar(final_message)
            
        self.__last_detected_objects = objetos_actuales.copy()

    def iniciar(self):
        """Inicia el ciclo principal del asistente."""
        
        # 1. Iniciar cámara y voz
        if not self.__camara.iniciar():
            print("[ERROR] No se pudo iniciar el asistente sin la cámara.")
            return

        self.__voz.hablar("Iniciando asistente visual y háptico. Presiona control c para salir.")
        
        # 2. Iniciar hilos de TFmini3 y control de motores
        self.__iniciar_hilos_tfmini()
        
        # 3. Bucle principal de detección visual
        try:
            while True:
                frame = self.__camara.capturar_frame()
                if frame is None:
                    time.sleep(1)
                    continue
                
                # Proceso de detección de objetos
                objetos_actuales = self.__ia.analizar_imagen(frame)
                self.__anunciar_detecciones(objetos_actuales)
                
                time.sleep(0.1) # Pequeña pausa para gestionar el CPU

        except KeyboardInterrupt:
            print("\n[INFO] Señal de interrupción recibida. Terminando programa.")
        except Exception as e:
            print(f"[ERROR] Ocurrió un error inesperado: {e}")
            
        finally:
            self.__camara.detener()
            pwm1.stop()
            pwm2.stop()
            GPIO.cleanup()
            print("[INFO] Sistema de detección y control háptico detenido.")

def main():
    """Función de inicio del programa."""
    asistente = AsistenteCombinado()
    asistente.iniciar()

if __name__ == "__main__":
    main()
