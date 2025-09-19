# -*- coding: utf-8 -*-
import time
import pigpio
from TFtest3 import distancias

# Configuración de los tres pins PWM
PIN_PWM_1 = 18  # Pin para UART1
PIN_PWM_2 = 19  # Pin para UART2
PIN_PWM_3 = 20  # Pin para UART3
FRECUENCIA_PWM = 1000

# Configuración de distancias
DISTANCIA_MIN = 10    # cm - PWM máximo (100%)
DISTANCIA_MAX = 400   # cm - PWM mínimo (0%)

def configurar_pwm():
    """Configura los tres pins PWM usando pigpio"""
    pi = pigpio.pi()
    
    # Configurar frecuencia para los tres pins
    pi.set_PWM_frequency(PIN_PWM_1, FRECUENCIA_PWM)
    pi.set_PWM_frequency(PIN_PWM_2, FRECUENCIA_PWM)
    pi.set_PWM_frequency(PIN_PWM_3, FRECUENCIA_PWM)
    
    # Iniciar con duty cycle 0 en todos los pins
    pi.set_PWM_dutycycle(PIN_PWM_1, 0)
    pi.set_PWM_dutycycle(PIN_PWM_2, 0)
    pi.set_PWM_dutycycle(PIN_PWM_3, 0)
    
    return pi

def calcular_pwm(distancia):
    """Calcula el duty cycle PWM basado en la distancia"""
    if distancia is None or distancia <= 0:
        return 0
    elif distancia <= DISTANCIA_MIN:
        return 100
    elif distancia >= DISTANCIA_MAX:
        return 0
    else:
        # Mapeo lineal: menor distancia = mayor PWM
        pwm = 100 - ((distancia - DISTANCIA_MIN) / (DISTANCIA_MAX - DISTANCIA_MIN)) * 100
        return int(pwm)

def control_pwm_uart1():
    """Control PWM para UART1"""
    distancia = distancias.get("uart1")
    duty_cycle = calcular_pwm(distancia)
    pwm_value = int((duty_cycle / 100.0) * 255)
    return duty_cycle, pwm_value, distancia

def control_pwm_uart2():
    """Control PWM para UART2"""
    distancia = distancias.get("uart2")
    duty_cycle = calcular_pwm(distancia)
    pwm_value = int((duty_cycle / 100.0) * 255)
    return duty_cycle, pwm_value, distancia

def control_pwm_uart3():
    """Control PWM para UART3"""
    distancia = distancias.get("uart3")
    duty_cycle = calcular_pwm(distancia)
    pwm_value = int((duty_cycle / 100.0) * 255)
    return duty_cycle, pwm_value, distancia

def main():
    print("Control PWM con Tres UARTs TFmini (pigpio)")
    print(f"Pin PWM UART1: {PIN_PWM_1} | Pin PWM UART2: {PIN_PWM_2} | Pin PWM UART3: {PIN_PWM_3}")
    print(f"Frecuencia: {FRECUENCIA_PWM} Hz")
    print(f"Distancia {DISTANCIA_MIN}-{DISTANCIA_MAX} cm")
    print("Presiona Ctrl+C para detener")
    
    # Configurar PWM
    pi = configurar_pwm()
    
    try:
        print("Iniciando control PWM para los tres UARTs...")
        
        while True:
            # Control PWM para UART1
            duty1, pwm1, dist1 = control_pwm_uart1()
            pi.set_PWM_dutycycle(PIN_PWM_1, pwm1)
            
            # Control PWM para UART2
            duty2, pwm2, dist2 = control_pwm_uart2()
            pi.set_PWM_dutycycle(PIN_PWM_2, pwm2)
            
            # Control PWM para UART3
            duty3, pwm3, dist3 = control_pwm_uart3()
            pi.set_PWM_dutycycle(PIN_PWM_3, pwm3)
            
            # Mostrar información de los tres UARTs
            print(f"UART1: {dist1} cm | PWM: {duty1}%")
            print(f"UART2: {dist2} cm | PWM: {duty2}%")
            print(f"UART3: {dist3} cm | PWM: {duty3}%")
            print("-" * 40)
            
            time.sleep(0.1)  # Actualizar cada 100ms
    
    except KeyboardInterrupt:
        print("\nDeteniendo...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Limpiar recursos pigpio
        pi.set_PWM_dutycycle(PIN_PWM_1, 0)
        pi.set_PWM_dutycycle(PIN_PWM_2, 0)
        pi.set_PWM_dutycycle(PIN_PWM_3, 0)
        pi.stop()
        print("Recursos liberados")

if __name__ == '__main__':
    main()
