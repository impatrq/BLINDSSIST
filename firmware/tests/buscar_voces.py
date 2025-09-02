import pyttsx3
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    print(f"ID de voz: {voice.id}, Nombre: {voice.name}")