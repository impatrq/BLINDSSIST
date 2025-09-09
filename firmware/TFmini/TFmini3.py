# -*- coding: utf-8 -*-
import serial
import time

ser = serial.Serial("/dev/serial0", 115200, timeout=1)

def getTFminiData():
    if ser.in_waiting >= 9:
        recv = ser.read(9)
        if recv[0] == 0x59 and recv[1] == 0x59:  # cabecera válida
            low = recv[2]
            high = recv[3]
            distance = low + (high << 8)
            return distance
    return None

if __name__ == '__main__':
    try:
        while True:
            dist = getTFminiData()
            if dist is not None:
                print("Distancia:", dist, "cm", flush=True)
            time.sleep(0.01)
    except KeyboardInterrupt:
        ser.close()
