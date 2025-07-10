import cv2
import pyttsx3
import subprocess
import numpy as np
import signal
import sys
import os # Para verificar la existencia del modelo YOLO

# Importar YOLO 
from ultralytics import YOLO

# --- Configuración de Audio ---
# Inicializar motor de voz

try:
    voz = pyttsx3.init()
    # Ajustar la velocidad del habla
    voz.setProperty('rate', 150)
   
    voices = voz.getProperty('voices')
    found_spanish_voice = False
    for voice in voices:
        if 'es' in voice.languages or 'spanish' in voice.name.lower():
            voz.setProperty('voice', voice.id)
            found_spanish_voice = True
            break
    if not found_spanish_voice:
        print("[ADVERTENCIA] No se encontró una voz en español. Se usará la voz predeterminada.")

    print("[INFO] Motor de voz inicializado.")
except Exception as e:
    print(f"[ERROR] No se pudo inicializar el motor de voz: {e}")
    print("Asegúrate de tener 'espeak' instalado: sudo apt install espeak")
    sys.exit(1)


# --- Configuración del Modelo y Clases ---
# Ruta al modelo YOLOv8
MODELO_PATH = "yolov8n.pt" # Este archivo esté en el mismo directorio

if not os.path.exists(MODELO_PATH):
    print(f"[ERROR] El archivo del modelo '{MODELO_PATH}' no se encontró.")
    print("Por favor, descarga el modelo con: yolo detect train data=coco8.yaml model=yolov8n.pt epochs=1 imgsz=640 --weights yolov8n.pt")
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

# Clases permitidas para la detección, basadas en las claves del diccionario de traducción
clases_permitidas = list(traduccion.keys())
print(f"[INFO] Clases permitidas para detección: {clases_permitidas}")

# --- Variables de Detección ---
ultimos_objetos = {} # Para guardar la cantidad de cada objeto detectado anteriormente
CONFIDENCE_THRESHOLD = 0.6 # Puedes ajustar este valor (0.0 a 1.0) para menos/más detecciones

# --- Manejo de Señales para Salir ---
def salir_graciosamente(sig, frame):
    print("\n[INFO] Señal de interrupción recibida. Terminando programa.")
    voz.stop() # Detener el motor de voz
    sys.exit(0)

# Registrar el manejador para Ctrl+C
signal.signal(signal.SIGINT, salir_graciosamente)

# --- Función de Captura de Cámara (usando libcamera-still) ---
def capturar_frame():
    """
    Captura un solo frame de la Pi Camera usando libcamera-still
    y lo devuelve como un array de OpenCV.
    """
    try:
        
        command = [
            'libcamera-still', '-t', '1',
            '--width', '640', '--height', '480',
            '-o', '-', '--denoise', 'off',
            '--nopreview' # Asegura que no se muestre una ventana de vista previa
        ]
        proceso = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE # Capturo stderr para ver errores de libcamera
        )
        imagen_bytes, err = proceso.communicate() # Uso communicate para evitar deadlocks
        
        if proceso.returncode != 0:
            print(f"[ERROR] libcamera-still falló con código {proceso.returncode}. Mensaje: {err.decode('utf-8').strip()}")
            return None

        # libcamera-still produce imágenes JPEG por defecto.
        # cv2.imdecode puede leerlas directamente desde bytes.
        imagen_array = np.frombuffer(imagen_bytes, dtype=np.uint8)
        frame = cv2.imdecode(imagen_array, cv2.IMREAD_COLOR)

        if frame is None:
            print("[ERROR] cv2.imdecode no pudo decodificar la imagen. Bytes recibidos:", len(imagen_bytes))
        return frame

    except FileNotFoundError:
        print("[ERROR] 'libcamera-still' no encontrado. Asegúrate de que la cámara de la Pi esté configurada y libcamera instalado.")
        print("Puedes verificar con: which libcamera-still")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Fallo al capturar frame: {e}")
        return None

# --- Bucle Principal de Detección ---
print("\n[INFO] Iniciando detección de objetos. Presiona Ctrl+C para salir.")
voz.say("Iniciando detección de objetos.")
voz.runAndWait()

while True:
    frame = capturar_frame()
    if frame is None:
        # Ya se imprimió un error en capturar_frame, se continua al siguiente ciclo
        continue

    # Realizar detección con YOLO
    resultados = modelo(frame, verbose=False)[0] # verbose=False para no imprimir cada inferencia (evitar exceso de tomas)

    objetos_actuales = {} # Diccionario para las detecciones en el frame actual

    # Procesar resultados y filtrar por clases permitidas y confianza
    for box in resultados.boxes:
        clase_id = int(box.cls[0])
        clase_nombre = modelo.names[clase_id]
        confianza = float(box.conf[0])

        if clase_nombre in clases_permitidas and confianza > CONFIDENCE_THRESHOLD:
            objetos_actuales[clase_nombre] = objetos_actuales.get(clase_nombre, 0) + 1

    # --- Anunciar Detecciones ---
    anuncios_pendientes = []

    # Identificar objetos nuevos o cambios en cantidad
    for clase, cantidad in objetos_actuales.items():
        cantidad_anterior = ultimos_objetos.get(clase, 0)

        if cantidad != cantidad_anterior:
            nombre_es = traduccion.get(clase, clase)
            if cantidad == 1:
                mensaje = f"Una {nombre_es} detectada."
            else:
                mensaje = f"{cantidad} {nombre_es}s detectados."
            anuncios_pendientes.append(mensaje)
            ultimos_objetos[clase] = cantidad # Actualizar el estado para futuras comparaciones

    # Si hay anuncios, concatenarlos y decirlos
    if anuncios_pendientes:
        mensaje_final = ", ".join(anuncios_pendientes)
        print(f"[INFO] Anuncio: {mensaje_final}")
        voz.say(mensaje_final)
        voz.runAndWait() # Bloquea hasta que el habla termina

  
    cv2.waitKey(500) # Pausa de 500ms (2 FPS efectivos de detección)