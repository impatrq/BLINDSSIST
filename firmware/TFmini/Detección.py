# -*- coding: utf-8 -*-
import time
from TFmini3 import getTFminiData
import pigpio

# Configuración del pin PWM
PIN_PWM = 18
FRECUENCIA_PWM = 1000

# Configuración de distancias
DISTANCIA_MIN = 10    # cm - PWM máximo (100%)
DISTANCIA_MAX = 400   # cm - PWM mínimo (0%)

def configurar_pwm():
    """Configura el pin PWM usando pigpio"""
    pi = pigpio.pi()
    pi.set_PWM_frequency(PIN_PWM, FRECUENCIA_PWM)
    pi.set_PWM_dutycycle(PIN_PWM, 0)  # Iniciar con duty cycle 0
    return pi

def calcular_pwm(distancia):
    """Calcula el duty cycle PWM basado en la distancia"""
    if distancia <= DISTANCIA_MIN:
        return 100
    elif distancia >= DISTANCIA_MAX:
        return 0
    else:
        # Mapeo lineal: menor distancia = mayor PWM
        pwm = 100 - ((distancia - DISTANCIA_MIN) / (DISTANCIA_MAX - DISTANCIA_MIN)) * 100
        return int(pwm)

def main():
    print("Control PWM con Láser TFmini (pigpio)")
    print(f"Pin PWM: {PIN_PWM}")
    print(f"Frecuencia: {FRECUENCIA_PWM} Hz")
    print(f"Distancia {DISTANCIA_MIN}-{DISTANCIA_MAX} cm")
    print("Presiona Ctrl+C para detener")
    
    # Configurar PWM
    pi = configurar_pwm()
    
    try:
        print("Iniciando control PWM...")
        
        while True:
            # Usar la función del archivo TFmini3.py
            distance, strength = getTFminiData()
            
            # Calcular PWM
            duty_cycle = calcular_pwm(distance)
            
            # Convertir porcentaje a valor de 0-255 para pigpio
            pwm_value = int((duty_cycle / 100.0) * 255)
            pi.set_PWM_dutycycle(PIN_PWM, pwm_value)
            
            print(f"Distancia: {distance} cm | Fuerza: {strength} | PWM: {duty_cycle}%")
    
    except KeyboardInterrupt:
        print("\nDeteniendo...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Limpiar recursos pigpio
        pi.set_PWM_dutycycle(PIN_PWM, 0)
        pi.stop()
        print("Recursos liberados")

if __name__ == '__main__':
    main() 