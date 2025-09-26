import serial
import time
import threading

# Diccionario global para guardar las distancias
distancias = {
    "uart1": None,
    "uart2": None,
    "uart3": None,
}

def getTFminiData(port, key_name):
    ser = serial.Serial(port, 115200, timeout=1)
    
    while True:
        if ser.in_waiting > 8:
            recv = ser.read(9)
            if recv[0] == 0x59 and recv[1] == 0x59:  # cabecera válida
                low = recv[2]
                high = recv[3]
                distance = low + (high << 8)
                # Guardamos el valor en el diccionario global
                distancias[key_name] = distance
        time.sleep(0.01)  # evita 100% CPU

# Funciones separadas para cada UART (manteniendo formato)
def getTFminiData_uart1():
    getTFminiData("/dev/ttyUSB0", "uart1")

def getTFminiData_uart2():
    getTFminiData("/dev/ttyUSB1", "uart2")

def getTFminiData_uart3():
    getTFminiData("/dev/Serial0", "uart3")

if __name__ == '__main__':
    try:
        # Crear un hilo por cada lectura
        t1 = threading.Thread(target=getTFminiData_uart1, daemon=True)
        t2 = threading.Thread(target=getTFminiData_uart2, daemon=True)
        t3 = threading.Thread(target=getTFminiData_uart3, daemon=True)

        # Iniciar los hilos
        t1.start()
        t2.start()
        t3.start()

        # Bucle principal donde puedes usar los valores
        while True:
            print("UART1:", distancias["uart1"], "cm")
            print("UART2:", distancias["uart2"], "cm")
            print("UART3:", distancias["uart3"], "cm")
            print("-" * 30)
            time.sleep(1)

    except KeyboardInterrupt:
        print("Programa interrumpido por el usuario")
