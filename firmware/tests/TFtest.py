def getTFminiData(port, key_name):
    ser = serial.Serial(port, 115200, timeout=1)

    while True:
        if ser.in_waiting > 0:
            # Leer un byte a la vez hasta encontrar 0x59
            first_byte = ser.read(1)
            if first_byte == b'\x59':
                second_byte = ser.read(1)
                if second_byte == b'\x59':
                    # Tenemos cabecera válida -> leemos los 7 bytes restantes
                    frame = ser.read(7)
                    if len(frame) == 7:
                        low = frame[0]
                        high = frame[1]
                        distance = low + (high << 8)

                        # Opcional: calcular checksum para validar
                        checksum = (0x59 + 0x59 + sum(frame[:-1])) & 0xFF
                        if checksum == frame[-1]:
                            distancias[key_name] = distance
                        else:
                            print(f"[{key_name}] Checksum inválido, descartando trama")
        time.sleep(0.005)  # bajar carga de CPU
