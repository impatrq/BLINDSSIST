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