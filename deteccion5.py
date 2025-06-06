from ultralytics import YOLO
import cv2
import pyttsx3

# Inicializar motor de voz
voz = pyttsx3.init()
voz.setProperty('rate', 150)  # velocidad del habla

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

# Modelo y clases permitidas
modelo = YOLO("yolov8n.pt")
clases_permitidas = list(traduccion.keys())

# Cámara
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
pausado = False

# Para guardar la cantidad de cada objeto detectado anteriormente
ultimos_objetos = {}

while True:
    if not pausado:
        ret, frame = cap.read()
        if not ret:
            break

        resultados = modelo(frame)[0]
        cajas_filtradas = []
        objetos_actuales = {}

        # Contar objetos detectados
        for box in resultados.boxes:
            clase_id = int(box.cls[0])
            clase_nombre = modelo.names[clase_id]
            confianza = float(box.conf[0])

            if clase_nombre in clases_permitidas and confianza > 0.8:
                cajas_filtradas.append(box)

                if clase_nombre not in objetos_actuales:
                    objetos_actuales[clase_nombre] = 1
                else:
                    objetos_actuales[clase_nombre] += 1

        # Comparar con la detección anterior para decidir si anunciar
        for clase, cantidad in objetos_actuales.items():
            cantidad_anterior = ultimos_objetos.get(clase, 0)

            if cantidad != cantidad_anterior:
                ultimos_objetos[clase] = cantidad
                nombre_es = traduccion.get(clase, clase)
                if cantidad == 1:
                    voz.say(f"Una {nombre_es} detectada")
                else:
                    voz.say(f"{cantidad} {nombre_es}s detectados")
                voz.runAndWait()

        # Eliminar objetos que ya no están presentes
        for clase in list(ultimos_objetos):
            if clase not in objetos_actuales:
                del ultimos_objetos[clase]

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
