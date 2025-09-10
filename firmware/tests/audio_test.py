# audio_test.py
import pyttsx3

# Inicializar el motor de pyttsx3
engine = pyttsx3.init()

# Configurar la velocidad de la voz para mayor claridad
engine.setProperty('rate', 150)

# Configurar el volumen
engine.setProperty('volume', 0.9)


# voices = engine.getProperty('voices')
# for voice in voices:
#     if 'spanish' in voice.name.lower():
#         engine.setProperty('voice', voice.id)
#         break

# Texto que se va a reproducir
texto_a_hablar = "¡Prueba de audio exitosa! El sistema de sonido está funcionando correctamente."
print("Reproduciendo: " + texto_a_hablar)

# Reproducir el texto
engine.say(texto_a_hablar)

# Esperar a que el motor termine de hablar
engine.runAndWait()

print("Prueba de audio finalizada.")
