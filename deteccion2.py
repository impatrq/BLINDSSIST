from ultralytics import YOLO
import cv2
import pyttsx3

# Inicializar motor de voz
voz = pyttsx3.init()
voz.setProperty('rate', 150)  # velocidad del habla

# Cargar modelo YOLOv8 nano preentrenado
modelo = YOLO("yolov8n.pt")
clases_permitidas = ['person', 'car', 'bicycle', 'motorcycle', 'bus', 'truck']

# Inicializar cámara
cap = cv2.VideoCapture(1)
pausado = False
dicho_objetos = set()  # Para no repetir

while True:
    if not pausado:
        ret, frame = cap.read()
        if not ret:
            break

        resultados = modelo(frame)[0]

        # Filtrar clases
        cajas_filtradas = []
        for box in resultados.boxes:
            clase_id = int(box.cls[0])
            clase_nombre = modelo.names[clase_id]
            confianza = float(box.conf[0])

            if clase_nombre in clases_permitidas:
                cajas_filtradas.append(box)

                # Si es nuevo y > 0.8, anunciarlo
                if confianza > 0.8 and clase_nombre not in dicho_objetos:
                    print(f"Detectado: {clase_nombre} ({confianza:.2f})")
                    voz.say(f"{clase_nombre} detectado")
                    voz.runAndWait()
                    dicho_objetos.add(clase_nombre)

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
