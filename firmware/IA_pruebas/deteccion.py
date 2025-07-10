from ultralytics import YOLO
import cv2

# Cargar modelo preentrenado YOLOv8 nano
modelo = YOLO("yolov8n.pt")

# Captura de video (0 = webcam por defecto)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Inferencia del modelo
    resultados = modelo(frame)

    # Dibujar los resultados sobre el frame
    frame_anotado = resultados[0].plot()

    # Mostrar ventana
    cv2.imshow("Detección de obstáculos", frame_anotado)

    # Salir con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
