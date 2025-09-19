import time
import threading
import RPi.GPIO as GPIO
from TFmini3 import distancias, getTFminiData_uart1, getTFminiData_uart2, getTFminiData_uart3  # importamos lo que ya hiciste

# Pines PWM (hardware soportados en RPi4: GPIO18 y GPIO13)
MOTOR_PIN1 = 18   # PWM 1
MOTOR_PIN2 = 13   # PWM 2

GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTOR_PIN1, GPIO.OUT)
GPIO.setup(MOTOR_PIN2, GPIO.OUT)

# PWM iniciales: 100 Hz, duty cycle 30%
pwm1 = GPIO.PWM(MOTOR_PIN1, 100)
pwm2 = GPIO.PWM(MOTOR_PIN2, 100)

pwm1.start(30)
pwm2.start(30)

# ---------------- FUNCIONES DE CONTROL ----------------

def control_motor_uart1():
    """Control del motor basado en la primera lectura UART"""
    while True:
        d = distancias["uart1"]
        if d is not None:
            if d < 100:
                duty = min(100, 30 + (100 - d))
            else:
                duty = 30
            pwm1.ChangeDutyCycle(duty)
            print(f"[UART1] Distancia: {d} cm | Duty PWM1: {duty}%")
        time.sleep(0.1)


def control_motor_uart2():
    """Control del motor en pin GPIO13 si la distancia < 100 cm"""
    while True:
        d = distancias["uart2"]
        if d is not None:
            if d < 100:
                duty = min(100, 30 + (100 - d))
            else:
                duty = 30
            pwm2.ChangeDutyCycle(duty)
            print(f"[UART2] Distancia: {d} cm | Duty PWM2: {duty}%")
        time.sleep(0.1)


def control_motor_uart3():
    """PWM intercalado en ambos pines si la distancia < 100 cm"""
    toggle = True
    while True:
        d = distancias["uart3"]
        if d is not None:
            if d < 100:
                if toggle:
                    pwm1.ChangeDutyCycle(80)
                    pwm2.ChangeDutyCycle(0)
                else:
                    pwm1.ChangeDutyCycle(0)
                    pwm2.ChangeDutyCycle(80)
                toggle = not toggle
                print(f"[UART3] Distancia: {d} cm | PWM intercalado")
            else:
                pwm1.ChangeDutyCycle(30)
                pwm2.ChangeDutyCycle(30)
        time.sleep(0.3)  # velocidad del parpadeo/intercalado

# ---------------- MAIN ----------------

if __name__ == "__main__":
    try:
        # hilos de lectura (el uart1 ya está implementado en TFtest3)
        t1 = threading.Thread(target=getTFminiData_uart1, daemon=True)
        t2 = threading.Thread(target=getTFminiData_uart2, daemon=True)
        t3 = threading.Thread(target=getTFminiData_uart3, daemon=True)

        t1.start()
        t2.start()
        t3.start()

        # hilos de control
        c1 = threading.Thread(target=control_motor_uart1, daemon=True)
        c2 = threading.Thread(target=control_motor_uart2, daemon=True)
        c3 = threading.Thread(target=control_motor_uart3, daemon=True)

        c1.start()
        c2.start()
        c3.start()

        # mantener el programa vivo
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Cerrando programa...")
    finally:
        pwm1.stop()
        pwm2.stop()
        GPIO.cleanup()