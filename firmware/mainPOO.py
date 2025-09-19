# main.py
from picamera2 import Picamera2
from ultralytics import YOLO
import cv2
import time
import subprocess
import signal
import sys
import os

# --- Configuración del Modelo y Clases ---
MODELO_PATH = "yolov8n.pt"

if not os.path.exists(MODELO_PATH):
    print(f"[ERROR] El archivo del modelo '{MODELO_PATH}' no se encontró.")
    print("Por favor, descarga el modelo y colócalo en el mismo directorio.")
    sys.exit(1)

try:
    modelo = YOLO(MODELO_PATH)
    print(f"[INFO] Modelo YOLOv8 cargado desde '{MODELO_PATH}'.")
except Exception as e:
    print(f"[ERROR] No se pudo cargar el modelo YOLOv8: {e}")
    sys.exit(1)

# Diccionario de traducción de clases al español
traduccion = {
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

# Clases permitidas para la detección
clases_permitidas = list(traduccion.keys())
print(f"[INFO] Clases permitidas para detección: {clases_permitidas}")

# Variables de Detección
ultimos_objetos = {}
CONFIDENCE_THRESHOLD = 0.6

# --- Funciones ---
def say_alert(message):
    """Llama a espeak para reproducir un mensaje de audio."""
    try:
        subprocess.run(['espeak', f'"{message}"'], check=True)
    except Exception as e:
        print(f"[ERROR] Fallo al reproducir audio con espeak: {e}")

# --- Bucle Principal de Detección ---
print("\n[INFO] Inicializando cámara y detección de objetos. Presiona Ctrl+C para salir.")
say_alert("Iniciando detección de objetos.")

# Inicializar cámara con Picamera2
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)

try:
    picam2.start()
    print("Cámara iniciada. El sistema BlindAssist está activo.")

    while True:
        frame = picam2.capture_array()
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        resultados = modelo(frame_bgr, verbose=False)[0]
        objetos_actuales = {}

        for box in resultados.boxes:
            clase_id = int(box.cls[0])
            clase_nombre = modelo.names[clase_id]
            confianza = float(box.conf[0])

            if clase_nombre in clases_permitidas and confianza > CONFIDENCE_THRESHOLD:
                objetos_actuales[clase_nombre] = objetos_actuales.get(clase_nombre, 0) + 1

        anuncios_pendientes = []
        for clase, cantidad in objetos_actuales.items():
            cantidad_anterior = ultimos_objetos.get(clase, 0)
            
            if cantidad != cantidad_anterior:
                nombre_es = traduccion.get(clase, clase)
                mensaje = f"Una {nombre_es} detectada." if cantidad == 1 else f"{cantidad} {nombre_es}s detectados."
                anuncios_pendientes.append(mensaje)
                ultimos_objetos[clase] = cantidad

        if anuncios_pendientes:
            mensaje_final = ", ".join(anuncios_pendientes)
            print(f"[INFO] Anuncio: {mensaje_final}")
            say_alert(mensaje_final)

        # Pequeña pausa para no sobrecargar el sistema
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n[INFO] Señal de interrupción recibida. Terminando programa.")
except Exception as e:
    print(f"[ERROR] Ocurrió un error inesperado: {e}")
    
finally:
    picam2.stop()
    print("[INFO] Sistema de detección detenido.")
