# main.py
from picamera2 import Picamera2
from ultralytics import YOLO
import cv2
import time
import subprocess

# --- Configuración ---
CONFIDENCE_THRESHOLD = 0.75
TARGET_CLASSES = ['person', 'car', 'bus', 'truck', 'bicycle', 'motorcycle']

# --- Inicialización ---
print("Inicializando componentes...")

# Inicializar cámara
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)

# Cargar el modelo YOLOv8n
model = YOLO('yolov8n.pt')

# Función para dar alertas de voz
def say_alert(message):
    print(f"Alerta: {message}")
    try:
        subprocess.run(['espeak', f'"{message}"'], check=True)
    except Exception as e:
        print(f"Error al reproducir audio con espeak: {e}")

# --- Bucle Principal ---
try:
    picam2.start()
    print("Cámara iniciada. El sistema BlindAssist está activo.")
    
    while True:
        frame = picam2.capture_array()
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        results = model(frame_bgr, verbose=False)

        for r in results:
            for box in r.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = model.names[class_id]
                
                if class_name in TARGET_CLASSES and confidence > CONFIDENCE_THRESHOLD:
                    say_alert(f"Cuidado, hay {class_name} cerca.")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nDeteniendo el sistema BlindAssist...")
    
finally:
    picam2.stop()
    print("Sistema BlindAssist detenido.")
