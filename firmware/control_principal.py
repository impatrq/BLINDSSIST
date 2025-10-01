# control_principal.py
import RPi.GPIO as GPIO
import threading
import time
import subprocess
import sys
import os
import cv2
from ultralytics import YOLO
from picamera2 import Picamera2
# --- Importación del módulo LiDAR (asume que está en TFmini3.py en el mismo dir) ---
try:
    from TFmini3 import distancias, getTFminiData_uart1, getTFminiData_uart2, getTFminiData_uart3
except ImportError:
    # Esto solo se imprimirá si la importación falla al inicio del sistema
    print("[ERROR] No se pudo importar TFmini3. Deteniendo programa.")
    sys.exit(1)


# --- CONFIGURACIÓN DE PINES Y ESTADO GLOBAL ---
PIN_DETECCION = 25     # Pin BCM para el botón de Detección de Objetos (GPIO 25)
PIN_LIDAR = 8          # Pin BCM para el botón de Advertencia de Obstáculos (GPIO 8)

# Variables de estado globales que controlan los bucles
deteccion_activa = False
lidar_activo = False

# --- VARIABLES LIDAR GLOBALES ---
MOTOR_PIN1 = 18    # PWM 1
MOTOR_PIN2 = 13    # PWM 2
pwm1 = None
pwm2 = None


# -----------------------------------------------------------
# --- MÓDULOS DE Detección de Objetos (POO) ---
# -----------------------------------------------------------

class Camara:
    """Controla la captura de frames de la cámara de la Raspberry Pi."""
    def __init__(self, width=640, height=480):
        self.__width = width
        self.__height = height
        self.__picam2 = None

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
    def hablar(self, texto):
        """Pronuncia el texto dado usando subprocess y espeak."""
        try:
            # Silenciar la salida de espeak en la terminal
            subprocess.run(['espeak', f'"{texto}"'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"[ERROR] Fallo al reproducir audio con espeak: {e}")

class Traductor:
    """Gestiona el diccionario de traducciones."""
    def __init__(self):
        self.__traducciones = {
            'person': 'persona', 'car': 'auto', 'bicycle': 'bicicleta',
            'motorcycle': 'moto', 'bus': 'colectivo', 'truck': 'camión',
            'cell phone': 'celular', 'bottle': 'botella', 'tv': 'televisor'
        }
    def traducir(self, palabra_ingles):
        return self.__traducciones.get(palabra_ingles, palabra_ingles)
    def obtener_clases_permitidas(self):
        return list(self.__traducciones.keys())

class IA:
    """Analiza las imágenes usando el modelo YOLOv8."""
    def __init__(self, model_path, confidence_threshold, allowed_classes):
        if not os.path.exists(model_path):
            # Lanza excepción si el archivo no existe
            raise FileNotFoundError(f"[ERROR] El archivo del modelo '{model_path}' no se encontró.")
        self.__model = YOLO(model_path)
        self.__confidence_threshold = confidence_threshold
        self.__allowed_classes = allowed_classes
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


# -----------------------------------------------------------
# --- FUNCIONES DE CONTROL GLOBAL ---
# -----------------------------------------------------------

def iniciar_gpio():
    """Configura los pines GPIO para botones y PWM."""
    global pwm1, pwm2
    
    # Configuración de Botones (GPIO 25 y 8)
    GPIO.setmode(GPIO.BCM)
    # Configurar con pull-up para conectar el botón a GND
    GPIO.setup(PIN_DETECCION, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(PIN_LIDAR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # Agregar interrupción de evento (FALLING = botón presionado)
    GPIO.add_event_detect(PIN_DETECCION, GPIO.FALLING, callback=boton_callback, bouncetime=300)
    GPIO.add_event_detect(PIN_LIDAR, GPIO.FALLING, callback=boton_callback, bouncetime=300)
    
    # Configuración de PWM (Motores)
    GPIO.setup(MOTOR_PIN1, GPIO.OUT)
    GPIO.setup(MOTOR_PIN2, GPIO.OUT)
    pwm1 = GPIO.PWM(MOTOR_PIN1, 100) # Frecuencia de 100 Hz
    pwm2 = GPIO.PWM(MOTOR_PIN2, 100)
    pwm1.start(0)
    pwm2.start(0)

def detener_pwm():
    """Detiene todos los PWM y limpia GPIO."""
    if pwm1: pwm1.stop()
    if pwm2: pwm2.stop()
    GPIO.cleanup()


# -----------------------------------------------------------
# --- LÓGICA DE THREADS ---
# -----------------------------------------------------------

def ejecutar_deteccion_objetos():
    """Lógica principal de la Detección de Objetos, corre en un Thread."""
    global deteccion_activa
    
    traductor = Traductor()
    voz = Voz()
    
    try:
        camara = Camara()
        ia = IA(
            model_path="yolov8n.pt",
            confidence_threshold=0.6,
            allowed_classes=traductor.obtener_clases_permitidas()
        )
        if not camara.iniciar():
            deteccion_activa = False # Falla al iniciar la camara, salir
            return
        
        last_detected_objects = {}
        voz.hablar("Detección de objetos encendida.")
        print("[INFO] Bucle de Detección de Objetos INICIADO.")

        while deteccion_activa:
            frame = camara.capturar_frame()
            if frame is None:
                time.sleep(0.5)
                continue
            
            objetos_actuales = ia.analizar_imagen(frame)
            
            # --- Lógica de Anuncios ---
            anuncios = []
            
            # 1. Objetos nuevos o cambio de cantidad
            for class_name, count in objetos_actuales.items():
                last_count = last_detected_objects.get(class_name, 0)
                if count != last_count:
                    spanish_name = traductor.traducir(class_name)
                    # Formato singular/plural
                    message = f"Una {spanish_name} detectada." if count == 1 else f"{count} {spanish_name}s detectados."
                    anuncios.append(message)
            
            # 2. Objetos que ya no están
            for class_name, last_count in last_detected_objects.items():
                if class_name not in objetos_actuales and last_count > 0:
                    spanish_name = traductor.traducir(class_name)
                    message = f"Ya no hay {spanish_name}s."
                    anuncios.append(message)

            if anuncios:
                final_message = ", ".join(anuncios)
                print(f"[ANUNCIO DETECCION] {final_message}")
                voz.hablar(final_message)
                
            last_detected_objects = objetos_actuales.copy()
            time.sleep(0.1) # Pequeña pausa para rendimiento

    except FileNotFoundError as e:
        print(e)
        voz.hablar("Error. No se encontró el archivo del modelo YOLO.")
    except Exception as e:
        print(f"[ERROR CRÍTICO DETECCION] {e}")
        
    finally:
        # Asegurarse de detener la cámara al salir del bucle
        if 'camara' in locals():
            camara.detener()
        print("[INFO] Detección de Objetos DETENIDA.")
        voz.hablar("Detección de objetos apagada.")


# --- LÓGICA DE ADVERTENCIA DE OBSTÁCULOS (LiDAR) ---

def control_motor_uart1():
    """Control PWM para UART1 (Distancia < 120cm = más vibración)"""
    while lidar_activo:
        d = distancias.get("uart1")
        if d is not None:
            if d < 120:
                duty = min(100, (120 - d)) # Duty Cycle entre 0 y 100
            else:
                duty = 0
            pwm1.ChangeDutyCycle(duty)
        time.sleep(0.1)

def control_motor_uart2():
    """Control PWM para UART2"""
    while lidar_activo:
        d = distancias.get("uart2")
        if d is not None:
            if d < 120:
                duty = min(100, (120 - d))
            else:
                duty = 0
            pwm2.ChangeDutyCycle(duty)
        time.sleep(0.1)

def control_motor_uart3():
    """PWM Intercalado para UART3 (Aviso de frente/centro)"""
    toggle = True
    while lidar_activo:
        d = distancias.get("uart3")
        if d is not None:
            if d < 120:
                if toggle:
                    pwm1.ChangeDutyCycle(80)
                    pwm2.ChangeDutyCycle(0)
                else:
                    pwm1.ChangeDutyCycle(0)
                    pwm2.ChangeDutyCycle(80)
                toggle = not toggle
            else:
                pwm1.ChangeDutyCycle(0)
                pwm2.ChangeDutyCycle(0)
        time.sleep(0.3) # Velocidad de intermitencia/parpadeo

def ejecutar_advertencia_obstaculos():
    """Lógica principal de LiDAR, corre en un Thread."""
    global lidar_activo
    voz = Voz()
    
    # Hilos de lectura UART (Se ejecutan en segundo plano y actualizan el diccionario 'distancias')
    t1 = threading.Thread(target=getTFminiData_uart1, daemon=True)
    t2 = threading.Thread(target=getTFminiData_uart2, daemon=True)
    t3 = threading.Thread(target=getTFminiData_uart3, daemon=True)
    
    # Hilos de control PWM (Leen 'distancias' y ajustan los motores)
    c1 = threading.Thread(target=control_motor_uart1, daemon=True)
    c2 = threading.Thread(target=control_motor_uart2, daemon=True)
    c3 = threading.Thread(target=control_motor_uart3, daemon=True)

    try:
        t1.start()
        t2.start()
        t3.start()
        c1.start()
        c2.start()
        c3.start()
        
        voz.hablar("Advertencia de obstáculos encendida.")
        print("[INFO] Advertencia de Obstáculos (LiDAR) INICIADA.")

        # Este bucle mantiene el thread vivo mientras los hilos de lectura y control trabajan
        while lidar_activo:
            time.sleep(1)

    except Exception as e:
        print(f"[ERROR CRÍTICO LIDAR] {e}")
        
    finally:
        # Asegurarse de que los motores se detengan al salir
        if pwm1: pwm1.ChangeDutyCycle(0)
        if pwm2: pwm2.ChangeDutyCycle(0)
        print("[INFO] Advertencia de Obstáculos (LiDAR) DETENIDA.")
        voz.hablar("Advertencia de obstáculos apagada.")


# -----------------------------------------------------------
# --- CALLBACK Y MAIN PRINCIPAL DE ARRANQUE ---
# -----------------------------------------------------------

def boton_callback(channel):
    """Función que se llama al presionar un botón (GPIO 25 o 8)."""
    global deteccion_activa, lidar_activo
    
    if channel == PIN_DETECCION:
        if not deteccion_activa:
            # Activar: Iniciar la detección en un nuevo Thread
            deteccion_activa = True
            thread = threading.Thread(target=ejecutar_deteccion_objetos)
            thread.start()
        else:
            # Desactivar: La bandera en False detiene el bucle del thread
            deteccion_activa = False
            
    elif channel == PIN_LIDAR:
        if not lidar_activo:
            # Activar: Iniciar el control LiDAR en un nuevo Thread
            lidar_activo = True
            thread = threading.Thread(target=ejecutar_advertencia_obstaculos)
            thread.start()
        else:
            # Desactivar: La bandera en False detiene el bucle del thread
            lidar_activo = False

def main():
    """Función principal de arranque y control de la Raspberry Pi."""
    
    # --- PAUSA AÑADIDA PARA EVITAR RuntimeError DE GPIO EN EL ARRANQUE ---
    print("[INFO] Esperando 10 segundos para asegurar la inicialización del sistema...")
    time.sleep(10)
    # ------------------------------------------------------------------
    
    iniciar_gpio()
    voz = Voz()
    
    print("Sistema de control iniciado. Esperando la pulsación de botones...")
    voz.hablar("Sistema listo para operar.")
    
    try:
        # El bucle principal mantiene el script de control vivo para escuchar los botones.
        while True:
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n[INFO] Señal de interrupción recibida. Terminando programa.")
    
    finally:
        # Limpieza de todos los recursos al finalizar (Ctrl+C o error)
        global deteccion_activa, lidar_activo
        deteccion_activa = False
        lidar_activo = False
        time.sleep(1) # Dar tiempo a los threads para que finalicen sus bucles
        detener_pwm()
        sys.exit(0)

if __name__ == "__main__":
    main()
