import pyttsx3

voz = pyttsx3.init(driverName='sapi5')  # Motor para Windows
voz.setProperty('rate', 150)
voz.setProperty('volume', 1.0)

voz.say("Hola, prueba de voz")
voz.runAndWait()
