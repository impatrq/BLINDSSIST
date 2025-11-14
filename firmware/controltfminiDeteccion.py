import time
import threading
import RPi.GPIO as GPIO
import subprocess
import sys
import os
import cv2
from picamera2 import Picamera2
from ultralytics import YOLO

# Módulo para sensores TFmini3 y diccionario compartido 'distancias'
try:
    from TFmini3 import distancias, getTFminiData_uart1, getTFminiData_uart2, getTFminiData_uart3
except ImportError:
    # Simula valores de distancia y funciones si la importación falla
    distancias = {"uart1": 200, "uart2": 200, "uart3": 200}
    def getTFminiData_uart1(): time.sleep(1)
    def getTFminiData_uart2(): time.sleep(1)
    def getTFminiData_uart3(): time.sleep(1)


# Configuración de pines de hardware para motores
MOTOR_PIN1 = 12     # PWM 1
MOTOR_PIN2 = 13     # PWM 2

BUTTON_HAPTIC_PIN = 8    # Botón para activar/desactivar control háptico
BUTTON_VISUAL_PIN = 25   # Botón para activar/desactivar detección visual

GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTOR_PIN1, GPIO.OUT)
GPIO.setup(MOTOR_PIN2, GPIO.OUT)
GPIO.setup(BUTTON_HAPTIC_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_VISUAL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Inicialización de PWM
pwm1 = GPIO.PWM(MOTOR_PIN1, 100)
pwm2 = GPIO.PWM(MOTOR_PIN2, 100)
pwm1.start(0)
pwm2.start(0)


# ====================================================================
# VARIABLES DE ESTADO Y BOTONES
# ====================================================================

estado_haptico_activo = False
estado_visual_activo = False

# Variables para Polling: mantienen el estado anterior del botón
last_haptic_state = GPIO.HIGH
last_visual_state = GPIO.HIGH


# Las funciones toggle_haptico y toggle_visual se han eliminado ya que 
# la lógica de toggle ahora está en el hilo de Polling.

# ====================================================================
# LÓGICA DE CONTROL HÁPTICO (LiDAR)
# ... [Lógica de control_sensores() NO ALTERADA] ...
# ====================================================================

def calcular_duty(d):
    """Convierte la distancia (cm) a ciclo de trabajo (duty cycle) de 0% a 100%."""
    if d is None or d >= 120:
        return 0
    return min(100, 120 - d)

def control_sensores():
    """Ejecuta el bucle principal que aplica el PWM a los motores según las reglas de proximidad."""
    global estado_haptico_activo
    toggle1 = False
    toggle2 = False
    
    while True:
        # 1. INICIALIZACIÓN: Los motores se apagan por defecto
        pwm1.ChangeDutyCycle(0)
        pwm2.ChangeDutyCycle(0)

        # Si el modo háptico está desactivado, salta la lógica
        if not estado_haptico_activo:
            time.sleep(0.1)
            continue
        
        # Bandera para saber si se ha detectado peligro
        peligro_detectado = False 

        d1 = distancias.get("uart1")
        d2 = distancias.get("uart2")
        d3 = distancias.get("uart3")

        duty1 = calcular_duty(d1)
        duty2 = calcular_duty(d2)
        duty3 = calcular_duty(d3)
        
        # =========================================================
        # REGLAS DE PROXIMIDAD (De la más restrictiva a la menos)
        # =========================================================

        # 1. CASO 6: LOS TRES < 120 (Máxima alerta)
        if all(d is not None and d < 120 for d in [d1, d2, d3]):
            pwm1.ChangeDutyCycle(100)
            pwm2.ChangeDutyCycle(100)
            peligro_detectado = True
        
        # 2. CASO 4: UART2 y UART3 <120 (Titila Motor 2)
        elif (d2 is not None and d2 < 120) and (d3 is not None and d3 < 120):
            toggle2 = not toggle2
            pwm2.ChangeDutyCycle(duty2 if toggle2 else 0)
            pwm1.ChangeDutyCycle(0) # Asegura el estado del otro motor
            time.sleep(0.3) # Mantén el sleep para el efecto de titileo
            peligro_detectado = True
        
        # 3. CASO 5: UART1 y UART3 <120 (Titila Motor 1)
        elif (d1 is not None and d1 < 120) and (d3 is not None and d3 < 120):
            toggle1 = not toggle1
            pwm1.ChangeDutyCycle(duty1 if toggle1 else 0)
            pwm2.ChangeDutyCycle(0) # Asegura el estado del otro motor
            time.sleep(0.3) # Mantén el sleep para el efecto de titileo
            peligro_detectado = True

        # 4. CASO 3: SOLO UART3 <120 (Ambos motores iguales)
        elif d3 is not None and d3 < 120:
            pwm1.ChangeDutyCycle(duty3)
            pwm2.ChangeDutyCycle(duty3)
            peligro_detectado = True
            
        # 5. CASOS 1 y 2: Comportamiento individual (si no se cumplen los casos anteriores)
        else: 
            if d1 is not None and d1 < 120:
                pwm1.ChangeDutyCycle(duty1)
                peligro_detectado = True
                
            if d2 is not None and d2 < 120:
                pwm2.ChangeDutyCycle(duty2)
                peligro_detectado = True
        

        # Retraso normal del bucle. Usamos 0.1s o el tiempo del titileo
        if not peligro_detectado:
              time.sleep(0.1)

# ====================================================================
# MÓDULOS DE DETECCIÓN VISUAL (Clases)
# ... [El resto de las clases Camara, Voz, Traductor, IA, AsistentePrincipal NO ALTERADAS] ...
# ====================================================================

class Camara:
    """Gestiona la captura de frames de video de la Picamera2."""
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
            return True
        except Exception:
            return False

    def detener(self):
        """Detiene el stream."""
        if self.__picam2:
            self.__picam2.stop()

    def capturar_frame(self):
        """Captura un frame y lo convierte a formato BGR (OpenCV)."""
        if self.__picam2:
            frame = self.__picam2.capture_array()
            return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return None

class Voz:
    """Maneja la síntesis de voz (espeak) de forma asíncrona para evitar bloquear la IA."""
    def __init__(self, velocidad=150):
        self.__velocidad = velocidad

    def hablar(self, texto):
        """Pronuncia el texto en un hilo separado."""
        try:
            command = ['espeak', f'-s {self.__velocidad}', f'"{texto}"', '-v', 'es']
            threading.Thread(target=lambda: subprocess.run(command, check=True), daemon=True).start()
        except Exception:
            pass # Ignora fallos si espeak no está disponible o falla

class Traductor:
    """Proporciona traducciones de nombres de objetos de YOLO (inglés a español)."""
    def __init__(self):
        self.__traducciones = {
            'person': 'persona', 'car': 'auto', 'bicycle': 'bicicleta', 'motorcycle': 'moto',
            'bus': 'colectivo', 'truck': 'camión', 'cell phone': 'celular', 'bottle': 'botella',
            'tv': 'televisor'
        }

    def traducir(self, palabra_ingles):
        """Traduce una palabra."""
        return self.__traducciones.get(palabra_ingles, palabra_ingles)
        
    def obtener_clases_permitidas(self):
        """Devuelve la lista de clases conocidas para el filtro de YOLO."""
        return list(self.__traducciones.keys())

class IA:
    """Carga y ejecuta el modelo YOLOv8 para la detección de objetos."""
    def __init__(self, model_path, confidence_threshold, allowed_classes):
        if not os.path.exists(model_path):
            sys.exit(1)
        try:
            self.__model = YOLO(model_path)
            self.__confidence_threshold = confidence_threshold
            self.__allowed_classes = allowed_classes
        except Exception:
            sys.exit(1)
            
    def analizar_imagen(self, frame):
        """Procesa un frame, filtra las detecciones por confianza y clase, y cuenta objetos."""
        results = self.__model(frame, verbose=False)[0]
        objetos_detectados = {}
        for box in results.boxes:
            class_id = int(box.cls[0])
            class_name = self.__model.names[class_id]
            confidence = float(box.conf[0])
            if class_name in self.__allowed_classes and confidence > self.__confidence_threshold:
                objetos_detectados[class_name] = objetos_detectados.get(class_name, 0) + 1
        return objetos_detectados

class AsistentePrincipal:
    """Orquesta la detección visual, la IA, la traducción y la voz."""
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
        """Compara detecciones con el estado anterior y genera anuncios de voz concisos."""
        anuncios = []
        
        # Anuncia objetos nuevos o cambios de cantidad
        for class_name, count in objetos_actuales.items():
            last_count = self.__last_detected_objects.get(class_name, 0)
            if count != last_count:
                spanish_name = self.__traductor.traducir(class_name)
                message = f"{count} {spanish_name}." if count > 1 else f"Una {spanish_name}."
                anuncios.append(message)
        
        # Anuncia objetos que desaparecieron
        for class_name, last_count in self.__last_detected_objects.items():
            if class_name not in objetos_actuales and last_count > 0:
                spanish_name = self.__traductor.traducir(class_name)
                message = f"{spanish_name} fuera."
                anuncios.append(message)

        if anuncios:
            final_message = " ".join(anuncios) 
            self.__voz.hablar(final_message)
            
        self.__last_detected_objects = objetos_actuales.copy()

    def iniciar_visual_loop(self):
        """Ejecuta el bucle principal de captura, análisis de IA y anuncio."""
        global estado_visual_activo
        if not self.__camara.iniciar():
            return

        self.__voz.hablar("Asistente combinado iniciado.")
        
        try:
            while True:
                if not estado_visual_activo:
                    time.sleep(0.1)
                    continue

                frame = self.__camara.capturar_frame()
                if frame is None:
                    time.sleep(1)
                    continue
                
                objetos_actuales = self.__ia.analizar_imagen(frame)
                self.__anunciar_detecciones(objetos_actuales)
                
                time.sleep(0.1) 

        except (KeyboardInterrupt, SystemExit):
            pass
        except Exception:
            pass
            
        finally:
            self.__camara.detener()


# ====================================================================
# NUEVA FUNCIÓN PARA POLLING DE BOTONES
# ====================================================================

def button_polling_loop():
    """Bucle de polling para manejar los botones con debounce por software."""
    global estado_haptico_activo, estado_visual_activo
    global last_haptic_state, last_visual_state
    
    # Tiempo de espera (debounce/sleep) entre chequeos
    POLLING_DELAY = 0.05 
    
    while True:
        # --- Lógica del Botón Háptico (LiDAR) ---
        haptic_input = GPIO.input(BUTTON_HAPTIC_PIN)
        
        # Detecta flanco de bajada (presionado)
        if haptic_input == GPIO.LOW and last_haptic_state == GPIO.HIGH:
            estado_haptico_activo = not estado_haptico_activo
            print(f"DEBUG Polling: Haptico activo: {estado_haptico_activo}")
            
        last_haptic_state = haptic_input
        
        # --- Lógica del Botón Visual (IA) ---
        visual_input = GPIO.input(BUTTON_VISUAL_PIN)
        
        # Detecta flanco de bajada (presionado)
        if visual_input == GPIO.LOW and last_visual_state == GPIO.HIGH:
            estado_visual_activo = not estado_visual_activo
            print(f"DEBUG Polling: Visual activo: {estado_visual_activo}")

        last_visual_state = visual_input

        time.sleep(POLLING_DELAY)


# ====================================================================
# FUNCIÓN PRINCIPAL (MAIN)
# ====================================================================

def main():
    """Configura e inicia los hilos para el sistema háptico, visual y de polling."""
    
    asistente = AsistentePrincipal()
    
    try:
        # Inicia hilos para la lectura de los 3 LiDARs (UART)
        threading.Thread(target=getTFminiData_uart1, daemon=True).start()
        threading.Thread(target=getTFminiData_uart2, daemon=True).start()
        threading.Thread(target=getTFminiData_uart3, daemon=True).start()

        # 🚀 INICIA EL HILO DE POLLING DE BOTONES
        threading.Thread(target=button_polling_loop, daemon=True).start()
        # NOTA: Se eliminaron las llamadas a GPIO.add_event_detect

        # Inicia el hilo centralizado para el control de PWM (háptico)
        threading.Thread(target=control_sensores, daemon=True).start()
        
        # Inicia el hilo principal de detección visual (cámara e IA)
        threading.Thread(target=asistente.iniciar_visual_loop, daemon=True).start()

        # El programa principal se mantiene activo
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        pass
        
    finally:
        # Limpieza de hardware al finalizar
        pwm1.stop()
        pwm2.stop()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
