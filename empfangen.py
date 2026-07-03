#PREPARE:
# - In der Datei config.ini die Zugangsdaten anpassen!
#
# - "C:\Thonny\python.exe" -m pip install --upgrade pip
# - "C:\Thonny\python.exe" -m pip install paho-mqtt rich
#
#
# Thonny öffnen -> Werkzeuge -> Optionen: "Nur eine Instanz von Thonny zulassen" = AUS
# Thonny beenden
# Thonny einmal öffnen und empfangen.py starten
# Thonny ein zweites mal öffnen und senden.py starten

import configparser

import paho.mqtt.client as mqtt


# Konfiguration lesen
config = configparser.ConfigParser()
config.read("config.ini")

server = config["MQTT"]["server"]
port = config.getint("MQTT", "port")
username = config["MQTT"]["username"]
password = config["MQTT"]["password"]
topic = config["MQTT"]["topic"]
tls = config.getboolean("MQTT", "tls")


def verbunden(client: mqtt.Client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Mit MQTT-Broker verbunden.")
        print("Warte auf Nachrichten für:")
        print(topic)

        client.subscribe(topic, qos=1)
    else:
        print("Verbindung fehlgeschlagen:", reason_code)


def nachricht_empfangen(client, userdata, message):
    wert = message.payload.decode("utf-8")

    print()
    print("Nachricht empfangen:")
    print("Topic:", message.topic)
    print("Wert: ", wert)


# MQTT-Client erstellen
client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="schueler01-empfaenger"
)

client.username_pw_set(username, password)

if tls:
    client.tls_set()

client.on_connect = verbunden
client.on_message = nachricht_empfangen


# Verbinden und dauerhaft warten
print("Verbinde mit MQTT-Broker " + server + ":" + str(port) + "...")
client.connect(server, port, 60)

client.loop_forever()

