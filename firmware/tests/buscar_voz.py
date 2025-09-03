import pyttsx3
import sys

class Voz:
    """Maneja síntesis de voz"""
    def __init__(self):
        self.__engine = None
        try:
            # Inicializar el motor especificando el backend de espeak
            self.__engine = pyttsx3.init('espeak')
            self.__engine.setProperty('rate', 150)
            self._set_spanish_voice()
        except Exception as e:
            # Imprimir el error para depurar
            print(f"Error al inicializar el motor de voz: {e}")
            sys.exit(1)

    def _set_spanish_voice(self):
        if self.__engine is None:
            return
        voices = self.__engine.getProperty('voices')
        for voice in voices:
            # Tu lógica para encontrar la voz en español es correcta
            if 'es' in voice.languages or 'spanish' in voice.name.lower():
                self.__engine.setProperty('voice', voice.id)
                return

    def hablar(self, texto):
        """Pronuncia texto dado"""
        if self.__engine is not None:
            self.__engine.say(texto)
            self.__engine.runAndWait()
        
    def detener(self, wait=True):
        """Detiene motor de voz"""
        if self.__engine is not None:
            self.__engine.stop()

# --- Ejemplo de uso ---
if __name__ == "__main__":
    try:
        voz = Voz()
        voz.hablar("Hola, he logrado solucionar el error.")
    except SystemExit:
        print("El programa se cerró debido a un error.")