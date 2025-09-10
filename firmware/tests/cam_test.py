# cam_test.py
from picamera2 import Picamera2
import time
import cv2

# Inicializar el objeto Picamera2
picam2 = Picamera2()

# Configurar la cámara para la vista previa
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)

# Iniciar la cámara
picam2.start()

print("Cámara iniciada. Capturando un frame de prueba...")

# Esperar un momento para que la cámara se caliente
time.sleep(2)

try:
    # Capturar un frame de la cámara
    frame = picam2.capture_array()
    
    # Si la captura es exitosa, se imprime un mensaje
    if frame is not None:
        print("¡Captura de frame exitosa! La cámara funciona correctamente.")
    else:
        print("Error: No se pudo capturar un frame.")

except Exception as e:
    print(f"Ocurrió un error al capturar el frame: {e}")

finally:
    # Detener la cámara
    picam2.stop()
    print("Cámara detenida. Prueba finalizada.")
