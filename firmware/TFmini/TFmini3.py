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
        if ser.in_waiting > 0:
            # Buscar cabecera 0x59 0x59
            first_byte = ser.read(1)
            if first_byte == b'\x59':
                second_byte = ser.read(1)
                if second_byte == b'\x59':
                    # Leer los 7 bytes restantes
                    frame = ser.read(7)
                    if len(frame) == 7:
                        low = frame[0]
                        high = frame[1]
                        distance = low + (high << 8)

                        # Calcular checksum
                        checksum = (0x59 + 0x59 + sum(frame[:-1])) & 0xFF
                        if checksum == frame[-1]:
                            distancias[key_name] = distance
                        else:
                            print(f"[{key_name}] Checksum inválido, descartando trama")

        time.sleep(0.005)  # Evita uso excesivo de CPU

# Funciones separadas para cada UART
def getTFminiData_uart1():
    getTFminiData("/dev/ttyUSB0", "uart1")

def getTFminiData_uart2():
    getTFminiData("/dev/ttyUSB1", "uart2")

def getTFminiData_uart3():
    getTFminiData("/dev/ttyS0", "uart3")

if __name__ == '__main__':
    try:
        # Crear hilos para cada sensor
        t1 = threading.Thread(target=getTFminiData_uart1, daemon=True)
        t2 = threading.Thread(target=getTFminiData_uart2, daemon=True)
        t3 = threading.Thread(target=getTFminiData_uart3, daemon=True)

        # Iniciar los hilos
        t1.start()
        t2.start()
        t3.start()

        # Bucle principal para imprimir distancias
        while True:
            print("UART1:", distancias["uart1"], "cm")
            print("UART2:", distancias["uart2"], "cm")
            print("UART3:", distancias["uart3"], "cm")
            print("-" * 30)
            time.sleep(1)

    except KeyboardInterrupt:
        print("Programa interrumpido por el usuario")
