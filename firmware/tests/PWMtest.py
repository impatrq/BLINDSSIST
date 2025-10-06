import time
import threading
import RPi.GPIO as GPIO
from TFtest3 import distancias, getTFminiData_uart1, getTFminiData_uart2, getTFminiData_uart3

# Pines PWM (hardware soportados en RPi4: GPIO18 y GPIO13)
MOTOR_PIN1 = 18   # PWM 1
MOTOR_PIN2 = 13   # PWM 2

GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTOR_PIN1, GPIO.OUT)
GPIO.setup(MOTOR_PIN2, GPIO.OUT)

# PWM iniciales: 100 Hz, duty cycle en 0%
pwm1 = GPIO.PWM(MOTOR_PIN1, 100)
pwm2 = GPIO.PWM(MOTOR_PIN2, 100)
pwm1.start(0)
pwm2.start(0)

# ---------------- FUNCIONES AUXILIARES ----------------

def calcular_duty(d):
    """Escalado de distancia a duty cycle"""
    if d is None:
        return 0
    if d < 120:
        return min(100, 120 - d)
    return 0

# ---------------- LÓGICA PRINCIPAL DE CONTROL ----------------

def control_sensores():
    """Controla ambos motores según las combinaciones de distancias."""
    toggle1 = False
    toggle2 = False
    while True:
        # Reiniciar PWM por defecto cada ciclo
        pwm1.ChangeDutyCycle(0)
        pwm2.ChangeDutyCycle(0)

        d1 = distancias.get("uart1")
        d2 = distancias.get("uart2")
        d3 = distancias.get("uart3")

        duty1 = calcular_duty(d1)
        duty2 = calcular_duty(d2)
        duty3 = calcular_duty(d3)

        # --- CASO 6: LOS TRES < 120 ---
        if all(d is not None and d < 120 for d in [d1, d2, d3]):
            pwm1.ChangeDutyCycle(100)
            pwm2.ChangeDutyCycle(100)
            print(f"[ALERTA] Todos <120 cm | PWM1=100% PWM2=100%")
            time.sleep(0.1)
            continue

        # --- CASO 4: UART2 y UART3 <120 → Motor2 titila ---
        if (d2 is not None and d2 < 120) and (d3 is not None and d3 < 120):
            toggle2 = not toggle2
            pwm2.ChangeDutyCycle(duty2 if toggle2 else 0)
            print(f"[UART2+UART3] Motor2 titila | PWM2={duty2 if toggle2 else 0}%")
            time.sleep(0.3)
            continue

        # --- CASO 5: UART1 y UART3 <120 → Motor1 titila ---
        if (d1 is not None and d1 < 120) and (d3 is not None and d3 < 120):
            toggle1 = not toggle1
            pwm1.ChangeDutyCycle(duty1 if toggle1 else 0)
            print(f"[UART1+UART3] Motor1 titila | PWM1={duty1 if toggle1 else 0}%")
            time.sleep(0.3)
            continue

        # --- CASO 3: SOLO UART3 <120 → Ambos motores iguales ---
        if d3 is not None and d3 < 120:
            pwm1.ChangeDutyCycle(duty3)
            pwm2.ChangeDutyCycle(duty3)
            print(f"[UART3] Ambos motores iguales | PWM={duty3}%")
            time.sleep(0.1)
            continue

        # --- CASOS 1 y 2: comportamiento individual ---
        if d1 is not None and d1 < 120:
            pwm1.ChangeDutyCycle(duty1)
        if d2 is not None and d2 < 120:
            pwm2.ChangeDutyCycle(duty2)

        print(f"[UART1] {d1}cm PWM1={duty1}% | [UART2] {d2}cm PWM2={duty2}%")
        time.sleep(0.1)

# ---------------- MAIN ----------------

if __name__ == "__main__":
    try:
        # Hilos de lectura UART
        t1 = threading.Thread(target=getTFminiData_uart1, daemon=True)
        t2 = threading.Thread(target=getTFminiData_uart2, daemon=True)
        t3 = threading.Thread(target=getTFminiData_uart3, daemon=True)
        t1.start()
        t2.start()
        t3.start()

        # Hilo de control coordinado
        control_thread = threading.Thread(target=control_sensores, daemon=True)
        control_thread.start()

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Cerrando programa...")
    finally:
        pwm1.stop()
        pwm2.stop()
        GPIO.cleanup()
