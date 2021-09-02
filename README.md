# RaspberryPi-Kaifa-SmartMeter-Reader

# Überblick

Ziel der Umsetzung: 
Auslesen der M-Bus Kundenschnittstelle am KAIFA SmartMeter Zähler.

Realisierung:
Die Auslesung erfolgt mit einem Raspberry Pi 3. Der Key wird von einer key.txt Datei beim Programmstart eingelesen.
Im Programm kann man die Variable logging mit 1 setzen, um die 5sek Werte in eine Datei zu loggen.

Programmaufruf:
python3 kaifa_kundenschnittstelle_auslesen.py

# Bemerkungen
Python ist sehr empfindlich bei den Einrückungen – daher checken ob nach copy / paste alles richtig eingerückt ist. 

# Unterstützte SmartMeter

* Kaifa Ma110 1-Phasenzähler
* Kaifa MA309M 3-Phasenzähler


# Netzbetreiber

* [Tinetz](https://www.tinetz.at/)


# Für den Nachbau benötige Teile

* Raspberry3
* M-Bus Adapter: Um die Kundenschnittstelle auslesen zu können, benötigt man einen M-Bus Adapter. Dieser setzt die 32V Signale um, auf TTL Pegel.
 - Den Adapter kann man sich entweder selber bauen, oder als fertige Platine im Internet bestellen.
 - Selber bauen: https://pc-projekte.lima-city.de/MBus-Konverter.html
 - Fertig bestellen: https://www.mikroe.com/m-bus-slave-click
* Stecker Kundenschnittstelle: RJ12 Kabel
* USB Seriell Adapterkabel (wie in der Selbstbauanleitung angegeben) - man kann die Serielle Schnittstelle auch direkt am Raspi anstecken, 
  aber im Programm muß dann das Device angepasst werden (port='/dev/ttyUSB0' wird zu port='/dev/serial0').






