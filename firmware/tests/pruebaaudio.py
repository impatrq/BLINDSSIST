import subprocess
import threading
import os
import time

class Voz:
    """Maneja la síntesis de voz usando un único comando de shell (espeak | aplay) con shell=True."""
    
    def __init__(self, velocidad=115): 
        self.__velocidad = velocidad
        # Dispositivo USB que debe funcionar (hw:1,0)
        self.__ALSA_DEVICE = "hw:1,0" 
        print(f"[INFO] Módulo de Voz inicializado con comando único de shell a {self.__ALSA_DEVICE} (USB).")

    def hablar(self, texto):
        """Ejecuta la tubería espeak | aplay como un único comando de shell en un hilo."""
        
        # El comando se construye como una sola cadena de texto para el shell.
        # Es CRUCIAL que el texto vaya entre comillas simples para manejar frases con espacios.
        command = (
            f"espeak -s {self.__velocidad} -v es '{texto}' --stdout "
            f"| aplay -D {self.__ALSA_DEVICE} -t raw -f S16_LE -r 22050"
        )
        
        try:
            print(f"[COMANDO] Ejecutando Shell: {command}")

            # Usamos subprocess.run con shell=True para que el intérprete de comandos (bash) 
            # se encargue de la tubería, que es mucho más fiable que el manejo interno de Python.
            threading.Thread(
                target=lambda: subprocess.run(
                    command, 
                    shell=True,
                    check=False,
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL
                )
            ).start()
            
        except Exception as e:
            print(f"\n[ERROR] Fallo en la tubería de audio (Shell): {e}")

# --- Bloque de Prueba ---
def main_test():
    """Función principal para probar el audio."""
    voz = Voz()
    
    print("\n--- INICIO DE PRUEBAS ---")
    
    # 1. Primera prueba
    voz.hablar("Prueba final. Si esto funciona, el problema era la tubería de Python.")
    time.sleep(4) 

    # 2. Segunda prueba
    voz.hablar("Espero que escuches este mensaje por el puerto USB.")
    time.sleep(5)
    
    print("\n--- FIN DE PRUEBAS ---")

if __name__ == "__main__":
    main_test()
