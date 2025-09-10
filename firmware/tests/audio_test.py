# audio_test.py
import pyttsx3

# Inicializar el motor de pyttsx3. Especificamos el driver.
engine = pyttsx3.init(driverName='espeak')

# Configurar la velocidad y el volumen
engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)

# Texto que se va a reproducir
texto_a_hablar = "¡Prueba de audio exitosa! El sistema de sonido está funcionando correctamente."
print("Reproduciendo: " + texto_a_hablar)

# Reproducir el texto
engine.say(texto_a_hablar)

# Esperar a que el motor termine de hablar
engine.runAndWait()

print("Prueba de audio finalizada.")
