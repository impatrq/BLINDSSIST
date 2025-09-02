import pyttsx3

voz = pyttsx3.init(driverName='sapi5')  # Motor para Windows
voz.setProperty('rate', 150)
voz.setProperty('volume', 1.0)

voz.say("Hola, prueba de voz")
voz.runAndWait()


class Parlante:
    def __innit__(self):
        self.voz = pyttsx3.init(driverName='sapi5')  # Motor para Windows
        self.voz.setProperty('rate', 150)
        self.voz.setProperty('volume', 1.0)
    
    def Reproducir(self,palabra):
        if palabra not str:
            raise TypeError
        self.voz.say(palabra)
        self.voz.runAndWait()
        