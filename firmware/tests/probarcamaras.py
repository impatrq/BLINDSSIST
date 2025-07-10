import cv2

for i in range(5):  # Probá los puertos del 0 al 4
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"✅ Cámara encontrada en el puerto {i}")
        cap.release()
    else:
        print(f"❌ No hay cámara en el puerto {i}")
