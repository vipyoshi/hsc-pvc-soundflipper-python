import configparser
import time
import RPi.GPIO as GPIO
import subprocess
import random
import network
import launch

# Get Config-Parameters
config = configparser.ConfigParser()
config.read('./src/config.ini')
configParameters = config['ear']
configGPIO = config['gpio']

Trigger_OutputPin = int(configGPIO['Trigger_OutputPin'])
Echo_InputPin    = int(configGPIO['Echo_InputPin'])
sleeptime = float(configParameters['Sleeptime'])
distance = int(configParameters['Distance'])
carrier_Signal_Duration = float(configParameters['Carrier_Signal_Duration'])


def setup():
    random.seed()
    GPIO.setup(Trigger_OutputPin, GPIO.OUT)
    GPIO.setup(Echo_InputPin, GPIO.IN)
    GPIO.output(Trigger_OutputPin, False)

def onBallDetection():
    #score senden
    launch.setNewGameFalse()
    network.send(100)
    Zufallszahl = random.randrange(1,4)
    Datei = "audio/" + str(Zufallszahl) + ".mp3"
    subprocess.Popen(["mpg123", Datei])

def run():
    # Abstandsmessung wird mittels des 10us langen Triggersignals gestartet
    GPIO.output(Trigger_OutputPin, True)
    time.sleep(carrier_Signal_Duration)
    GPIO.output(Trigger_OutputPin, False)

    # Hier wird die Stopuhr gestartet
    EinschaltZeit = time.time()
    while GPIO.input(Echo_InputPin) == 0:
        EinschaltZeit = time.time() # Es wird solange die aktuelle Zeit gespeichert, bis das Signal aktiviert wird

    while GPIO.input(Echo_InputPin) == 1:
        AusschaltZeit = time.time() # Es wird die letzte Zeit aufgenommen, wo noch das Signal aktiv war

    # Die Differenz der beiden Zeiten ergibt die gesuchte Dauer
    Dauer = AusschaltZeit - EinschaltZeit
    # Mittels dieser kann nun der Abstand auf Basis der Schallgeschwindigkeit der Abstand berechnet werden
    Abstand = (Dauer * 34300) / 2

    # Überprüfung, ob der gemessene Wert innerhalb der zulässigen Entfernung liegt
    if Abstand < 2 or (round(Abstand) > 300):
        # Es wird davon ausgegangen, dass wenn der gemessene Wert außerhalb des Bereichs liegt, dass dann ein Ball
        # in das Ohr gefallen ist.
        #print("Abstand außerhalb des Messbereich")
        #print("------------------------------")
        onBallDetection()
    else:
        # Der Abstand wird auf zwei Stellen hinterm Komma formatiert
        Abstand = format((Dauer * 34300) / 2, '.2f')
        #print("Der Abstand beträgt:%s"%Abstand)
        #print("------------------------------")
        if float(Abstand) <= distance:
            onBallDetection()

    # Pause zwischen den einzelnen Messungen
    time.sleep(sleeptime)

