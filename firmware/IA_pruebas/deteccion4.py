from ultralytics import YOLO
import cv2
import pyttsx3

# Inicializar motor de voz
voz = pyttsx3.init()
voz.setProperty('rate', 150)  # velocidad del habla

# Diccionario de traducción de clases de objetos de inglés a español
traduccion = {
    'person': 'persona',
    'car': 'auto',
    'bicycle': 'bicicleta',
    'motorcycle': 'moto',
    'bus': 'colctivo',
    'truck': 'camión',
    'cell phone': 'celular',
    'bottle': 'botella',
    'tv': 'televisor'
}

# Cargar modelo YOLOv8 nano preentrenado
modelo = YOLO("yolov8n.pt")
clases_permitidas = ['person', 'car', 'bicycle', 'motorcycle', 'bus', 'truck', 'cell phone', 'bottle', 'tv']

# Inicializar cámara
cap = cv2.VideoCapture(1)
pausado = False
dicho_objetos = {}  # Para llevar un registro de los objetos detectados y su cantidad

while True:
    if not pausado:
        ret, frame = cap.read()
        if not ret:
            break

        resultados = modelo(frame)[0]

        # Filtrar clases
        cajas_filtradas = []
        objetos_detectados = {}

        for box in resultados.boxes:
            clase_id = int(box.cls[0])
            clase_nombre = modelo.names[clase_id]
            confianza = float(box.conf[0])

            if clase_nombre in clases_permitidas:
                cajas_filtradas.append(box)

                # Contar la cantidad de objetos de la misma clase
                if confianza > 0.8:
                    if clase_nombre not in objetos_detectados:
                        objetos_detectados[clase_nombre] = 1
                    else:
                        objetos_detectados[clase_nombre] += 1

        # Anunciar los objetos detectados
        for clase_nombre, cantidad in objetos_detectados.items():
            if clase_nombre not in dicho_objetos:
                dicho_objetos[clase_nombre] = 0  # Inicializamos la cantidad

            if dicho_objetos[clase_nombre] != cantidad:
                dicho_objetos[clase_nombre] = cantidad

                # Traducir el nombre del objeto al español
                nombre_traducido = traduccion.get(clase_nombre, clase_nombre)  # Si no está en el diccionario, usa el nombre original

                # Si hay más de un objeto, mencionar la cantidad
                if cantidad == 1:
                    voz.say(f"Un {nombre_traducido} detectado")
                else:
                    voz.say(f"{cantidad} {nombre_traducido}s detectados")
                voz.runAndWait()

        resultados.boxes = cajas_filtradas
        frame_anotado = resultados.plot()

    cv2.imshow("Detección de obstáculos", frame_anotado)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('p'):
        pausado = not pausado

cap.release()
cv2.destroyAllWindows()
