import time
import threading
import RPi.GPIO as GPIO
from TFtest3 import distancias, getTFminiData_uart1  # importamos lo que ya hiciste

MOTOR_PIN = 18   # GPIO18 (pin físico 12)
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTOR_PIN, GPIO.OUT)

# PWM inicial: 100 Hz, duty cycle 30%
pwm = GPIO.PWM(MOTOR_PIN, 100)
pwm.start(30)

def control_motor():
    while True:
        d = distancias["uart1"]
        if d is not None:
            if d < 100:  
                # Si la distancia es < 100 cm, aumenta velocidad (más duty cycle)
                duty = min(100, 30 + (100 - d))  # duty entre 30% y 100%
            else:
                # Si está lejos, baja velocidad
                duty = 30  

            pwm.ChangeDutyCycle(duty)
            print(f"Distancia: {d} cm | Duty PWM: {duty}%")
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        # hilo para la lectura del TFmini
        t1 = threading.Thread(target=getTFminiData_uart1, daemon=True)
        t1.start()

        # bucle de control del motor
        control_motor()
    except KeyboardInterrupt:
        print("Cerrando programa...")
    finally:
        pwm.stop()
        GPIO.cleanup()