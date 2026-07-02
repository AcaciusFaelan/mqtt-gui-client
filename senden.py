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


# MQTT-Client erstellen
client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="schueler01-sender"
)

client.username_pw_set(username, password)

# Mit dem Broker verbinden
print(f"Verbinde mit MQTT-Broker {server}:{port} ...")

client.connect(server, port, 60)
client.loop_start()

try:
    # Immer wieder einen Wert abfragen
    while True:
        wert = input("LED-Wert eingeben (0 oder 1, sonst Ende): ").strip()

        nachricht = client.publish(
            topic,
            wert,
            qos=1,
            retain=True
        )

        nachricht.wait_for_publish()

        print("Gesendet:", wert)
except KeyboardInterrupt:
    # Verbindung beenden
    client.disconnect()
    client.loop_stop()

    print("\nMQTT-Verbindung beendet.")

