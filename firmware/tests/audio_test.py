import subprocess
import time

print("Probando la salida de audio...")

try:
    # Llama a espeak con un comando simple
    comando_espeak = ['espeak', "Hello, this is a test from Python."]
    subprocess.run(comando_espeak, check=True)
    print("Comando de espeak ejecutado correctamente.")

except FileNotFoundError:
    print("Error: El comando 'espeak' no se encontró. Asegúrate de que esté instalado.")
except Exception as e:
    print(f"Ocurrió un error: {e}")

print("Prueba finalizada.")
