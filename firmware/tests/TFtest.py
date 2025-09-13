# tfmini.py
import serial
import time

ser = serial.Serial("/dev/serial0", 115200, timeout=1)
distance = None  # variable global accesible desde otros módulos

def updateTFminiData():
    """Actualiza la variable global 'distance' con la última lectura válida"""
    global distance
    if ser.in_waiting >= 9:
        recv = ser.read(9)
        if recv[0] == 0x59 and recv[1] == 0x59:
            low = recv[2]
            high = recv[3]
            distance = low + (high << 8)

if __name__ == '__main__':
    try:
        while True:
            updateTFminiData()
            if distance is not None:
                print("Distancia:", distance, "cm", flush=True)
            time.sleep(0.01)
    except KeyboardInterrupt:
        ser.close()