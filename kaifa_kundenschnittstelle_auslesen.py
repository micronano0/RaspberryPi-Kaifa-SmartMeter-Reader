# Python3 Prog am Raspberry Pi
# Mbus-Adapter - die serielle Schnittstelle ist über ein Seriell zu USB Adapterkabel am Raspi angesteckt.
# der Key wird beim Programmstart aus der Datei key.txt gelesen.
# wenn die Variable logging auf 1 gesetzt wird, dann werden die 5sek Werte zusätzlich in eine Logdatei geschrieben.

from os import system, name
import time
from time import sleep
import binascii
import datetime
import serial
from Crypto.Cipher import AES



def clear():
    if name == 'nt':
        _ = system('cls')
  
    else:
        _ = system('clear')



# key lesen 
datei = open("key.txt", "r")
key = datei.read()
datei.close()
key=binascii.unhexlify(key)
#print (key)

# Daten in Logdatei schreiben
logging = 1 # wenn > 0 dann Logdatei schreiben

def recv(serial):
    while True:
        data = serial.read_all()
        if data == '':
            print ("\n...")
            continue
        else:
            print ("\n...lausche auf Schnittstelle")
            break
        sleep(6)
    return data

if __name__ == '__main__':
    serial = serial.Serial(
     port='/dev/ttyUSB0',
     baudrate = 2400,
     parity=serial.PARITY_EVEN,
     stopbits=serial.STOPBITS_ONE,
     bytesize=serial.EIGHTBITS
    )

    headerstart = "68fafa68"

    while True:

        sleep(5)
 
        data = recv(serial)
        doit = 0
        if (data != b'') & (len(data) >= 355):
            startbytes = data[0:4].hex()
            #print ("startbytes = ", startbytes)
            #print ("headerstart = ", headerstart)
            if (startbytes == headerstart):
                #print ("\nstartbytes und headerstart sind gleich\n")
                doit = 1
                #print ("Laenge von data = ", len(data))
            else:
                # now call function we defined above
                clear()
                print ("\n*** Synchronisierung laeuft ***\n")
                #print ("Laenge von data = ", len(data))
                serial.flushInput()
                sleep(.5)



        if doit == 1 :
            clear()
            print ("data: ", data.hex())
            msglen1 = int(hex(data[1]),16) # 1. FA --- 250 Byte
            print ("msg1: ", msglen1)

            header1 = 27
            header2 = 9

            splitinfo = data[6] # wenn hier 00, dann gibts noch eine Nachricht

            systitle = data[11:19] # hier steht der SysTitle --- 8 Bytes
            #print ("systitle:", systitle.hex() )

            ic = data[23:27] # hier steht der SysTitle --- 4 Bytes
            iv = systitle + ic # iv ist 12 Bytes
            #print ("iv= ", iv.hex() , "Länge: ", len(iv))

            #print ("\nmsg1:")
            msg1 = data[header1:(6+msglen1-2)]
            #print (msg1.hex())
            #print ("Länge: ",len(msg1))

            #print ("\nmsg2:")
            msglen2 = int(hex(data[msglen1+7]),16) # 1. FA --- 38 Byte
            #print ("msglen2: ", msglen2)
            #print (hex(data[msglen1+7]))

            msg2 = data[msglen1+6+header2:(msglen1+5+5+msglen2)]
            #print (msg2.hex())
            #print ("Länge msg2 :" ,len(msg2))


            cyphertext = msg1 + msg2
            #print ("\ncyphertext:")
            #print (cyphertext.hex())
            #print ("Länge: ",len(cyphertext))



            cyphertext_bytes=binascii.unhexlify(cyphertext.hex())
            cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
            decrypted = cipher.decrypt(cyphertext_bytes)

            #print("\nDecrypted:")
            #print(decrypted.hex())


            # OBIS Code Werte aus decrypted.hex auslesen

            databin = decrypted.hex()
            ueberschrift = ("\nOBIS Code\tBezeichnung\t\t\t Wert")
            print (ueberschrift)
            #print(databin)

            obis_len = 12


            # Datum Uhrzeit lesen
            # 0000010000ff

            obis_zeitstempel = '0000010000ff'
            obis_zeitstempel_offset = 4
            obis_zeitlaenge = 24
            obis_zeitstempel_pos = databin.find(obis_zeitstempel)
            if obis_zeitstempel_pos > 1:
                #print ("obis_zeitstempel_pos: ", obis_zeitstempel_pos)
                obis_datum_zeit = databin[obis_len + obis_zeitstempel_pos + obis_zeitstempel_offset:obis_len + obis_zeitstempel_pos + obis_zeitstempel_offset + obis_zeitlaenge]
                #print ("obis_datum_zeit: ", obis_datum_zeit)

                jahr = int(obis_datum_zeit[:4],16)
                #print ("jahr: ", jahr)
                monat = int(obis_datum_zeit[4:6],16)
                #print ("monat: ", monat)
                tag = int(obis_datum_zeit[6:8],16)
                #print ("tag: ", tag)
                stunde = int(obis_datum_zeit[10:12],16)
                #print ("stunde: ", stunde)
                minute = int(obis_datum_zeit[12:14],16)
                #print ("minute: ", minute)
                sekunde = int(obis_datum_zeit[14:16],16)
                #print ("sekunde: ", sekunde)

                obis_datum_zeit = datetime.datetime(jahr,monat,tag, stunde, minute, sekunde)
                datum_zeit = "0.0.1.0.0.255\tDatum Zeit:\t\t\t "+obis_datum_zeit.strftime("%d.%m.%Y %H:%M:%S")
                print (datum_zeit)
            
            else:
                #obis fehler
                datum_zeit = "\n*** kann OBIS Code nicht finden ===> key Fehler? ***\n"
                print (datum_zeit)


            # Zählernummer des Netzbetreibers
            # 0000600100ff

            obis_zaehlernummer = '0000600100ff'
            obis_zaehlernummer_pos = databin.find(obis_zaehlernummer)
            if obis_zaehlernummer_pos > 1:
                #print ("obis_zaehlernummer_pos: ", obis_zaehlernummer_pos)

                obis_zaehlernummer_anzzeichen = 2*int(databin[obis_zaehlernummer_pos+obis_len+2:obis_zaehlernummer_pos+obis_len+4],16)
                #print ("obis_zaehlernummer_anzzeichen: ", obis_zaehlernummer_anzzeichen)

                obis_zaehlernummer = databin[obis_zaehlernummer_pos+obis_len+4:obis_zaehlernummer_pos+obis_len+4+obis_zaehlernummer_anzzeichen]
                bytes_object = bytes.fromhex(obis_zaehlernummer)
                zaehlernummer = "0.0.96.1.0.255\tZaehlernummer:\t\t\t "+bytes_object.decode("ASCII")
                zaehlernummerfilename = bytes_object.decode("ASCII")
                print (zaehlernummer)



            # COSEM Logical Device Name
            # 00002a0000ff

            obis_cosemlogdevname = '00002a0000ff'
            obis_cosemlogdevname_pos = databin.find(obis_cosemlogdevname)
            if obis_cosemlogdevname_pos > 1:
                #print ("obis_cosemlogdevname_pos: ", obis_cosemlogdevname_pos)

                obis_cosemlogdevname_anzzeichen = 2*int(databin[obis_cosemlogdevname_pos+obis_len+2:obis_cosemlogdevname_pos+obis_len+4],16)
                #print ("obis_cosemlogdevname_anzzeichen: ", obis_cosemlogdevname_anzzeichen)

                obis_cosemlogdevname = databin[obis_cosemlogdevname_pos+obis_len+4:obis_cosemlogdevname_pos+obis_len+4+obis_cosemlogdevname_anzzeichen]
                bytes_object = bytes.fromhex(obis_cosemlogdevname)
                cosemlogdevname = "0.0.42.0.0.255\tCOSEM logical device name:\t "+bytes_object.decode("ASCII")
                print (cosemlogdevname)


            # Spannung L1 (V)
            # 0100200700ff

            obis_spannungl1 = '0100200700ff'
            obis_spannungl1_pos = databin.find(obis_spannungl1)
            #print ("obis_spannungl1_pos: ", obis_spannungl1_pos)
            if obis_spannungl1_pos > 1:

                obis_spannungl1_anzzeichen = 4
                obis_spannungl1 = databin[obis_spannungl1_pos+obis_len+2:obis_spannungl1_pos+obis_len+2+obis_spannungl1_anzzeichen]
                spannungl1 = "1.0.32.7.0.255\tSpannung L1 (V):\t\t "+str(int(obis_spannungl1,16)/10)
                print (spannungl1)

            # Spannung L2 (V)
            # 0100340700FF

            obis_spannungl2 = '0100340700ff'
            obis_spannungl2_pos = databin.find(obis_spannungl2)
            #print ("obis_spannungl2_pos: ", obis_spannungl2_pos)
            if obis_spannungl2_pos > 1:

                obis_spannungl2_anzzeichen = 4
                obis_spannungl2 = databin[obis_spannungl2_pos+obis_len+2:obis_spannungl2_pos+obis_len+2+obis_spannungl2_anzzeichen]
                spannungl2 = "1.0.52.7.0.255\tSpannung L2 (V):\t\t "+str(int(obis_spannungl2,16)/10)
                print (spannungl2)

            # Spannung L3 (V)
            # 0100480700ff

            obis_spannungl3 = '0100480700ff'
            obis_spannungl3_pos = databin.find(obis_spannungl3)
            #print ("obis_spannungl3_pos: ", obis_spannungl3_pos)
            if obis_spannungl3_pos > 1:

                obis_spannungl3_anzzeichen = 4
                obis_spannungl3 = databin[obis_spannungl3_pos+obis_len+2:obis_spannungl3_pos+obis_len+2+obis_spannungl3_anzzeichen]
                spannungl3 = "1.0.72.7.0.255\tSpannung L3 (V):\t\t "+str(int(obis_spannungl3,16)/10)
                print (spannungl3)


            # Strom L1 (A)
            # 01001f0700ff

            obis_stroml1 = '01001f0700ff'
            obis_stroml1_pos = databin.find(obis_stroml1)
            #print ("obis_stroml1_pos: ", obis_stroml1_pos)
            if obis_stroml1_pos > 1:

                obis_stroml1_anzzeichen = 4
                obis_stroml1 = databin[obis_stroml1_pos+obis_len+2:obis_stroml1_pos+obis_len+2+obis_stroml1_anzzeichen]
                stroml1 = "1.0.31.7.0.255\tStrom L1 (A):\t\t\t "+str(int(obis_stroml1,16)/100)
                print (stroml1)

            # Strom L2 (A)
            # 0100330700ff

            obis_stroml2 = '0100330700ff'
            obis_stroml2_pos = databin.find(obis_stroml2)
            #print ("obis_stroml2_pos: ", obis_stroml2_pos)
            if obis_stroml2_pos > 1:

                obis_stroml2_anzzeichen = 4
                obis_stroml2 = databin[obis_stroml2_pos+obis_len+2:obis_stroml2_pos+obis_len+2+obis_stroml2_anzzeichen]
                stroml2 = "1.0.51.7.0.255\tStrom L2 (A):\t\t\t "+str(int(obis_stroml2,16)/100)
                print (stroml2)

            # Strom L3 (A)
            # 0100470700ff

            obis_stroml3 = '0100470700ff'
            obis_stroml3_pos = databin.find(obis_stroml3)
            #print ("obis_stroml3_pos: ", obis_stroml3_pos)
            if obis_stroml3_pos > 1:

                obis_stroml3_anzzeichen = 4
                obis_stroml3 = databin[obis_stroml3_pos+obis_len+2:obis_stroml3_pos+obis_len+2+obis_stroml3_anzzeichen]
                stroml3 = "1.0.71.7.0.255\tStrom L3 (A):\t\t\t "+str(int(obis_stroml3,16)/100)
                print (stroml3)


            # Wirkleistung Bezug +P (W)
            # 0100010700ff

            obis_wirkleistungbezug = '0100010700ff'
            obis_wirkleistungbezug_pos = databin.find(obis_wirkleistungbezug)
            if obis_wirkleistungbezug_pos > 1:
                #print ("obis_wirkleistungbezug_pos: ", obis_wirkleistungbezug_pos)

                obis_wirkleistungbezug_anzzeichen = 8
                #print ("obis_wirkleistungbezug_anzzeichen: ", obis_wirkleistungbezug_anzzeichen)

                obis_wirkleistungbezug = databin[obis_wirkleistungbezug_pos+obis_len+2:obis_wirkleistungbezug_pos+obis_len+2+obis_wirkleistungbezug_anzzeichen]
                wirkleistungbezug = "1.0.1.7.0.255\tWirkleistung Bezug [kW]:\t "+str(int(obis_wirkleistungbezug,16)/1000)
                print (wirkleistungbezug)


            # Wirkleistung Lieferung -P (W)
            # 0100020700ff

            obis_wirkleistunglieferung = '0100020700ff'
            obis_wirkleistunglieferung_pos = databin.find(obis_wirkleistunglieferung)
            if obis_wirkleistunglieferung_pos > 1:
                #print ("obis_wirkleistunglieferung_pos: ", obis_wirkleistunglieferung_pos)

                obis_wirkleistunglieferung_anzzeichen = 8
                #print ("obis_wirkleistunglieferung_anzzeichen: ", obis_wirkleistunglieferung_anzzeichen)

                obis_wirkleistunglieferung = databin[obis_wirkleistunglieferung_pos+obis_len+2:obis_wirkleistunglieferung_pos+obis_len+2+obis_wirkleistunglieferung_anzzeichen]
                wirkleistunglieferung = "1.0.2.7.0.255\tWirkleistung Lieferung [kW]:\t "+str(int(obis_wirkleistunglieferung,16)/1000)
                print (wirkleistunglieferung)


            # Wirkenergie Bezug +A (Wh)
            # 0100010800ff

            obis_wirkenergiebezug = '0100010800ff'
            obis_wirkenergiebezug_pos = databin.find(obis_wirkenergiebezug)
            if obis_wirkenergiebezug_pos > 1:
                #print ("obis_wirkenergiebezug_pos: ", obis_wirkenergiebezug_pos)

                obis_wirkenergiebezug_anzzeichen = 8
                #print ("obis_wirkenergiebezug_anzzeichen: ", obis_wirkenergiebezug_anzzeichen)

                obis_wirkenergiebezug = databin[obis_wirkenergiebezug_pos+obis_len+2:obis_wirkenergiebezug_pos+obis_len+2+obis_wirkenergiebezug_anzzeichen]
                wirkenergiebezug = "1.0.1.8.0.255\tWirkenergie Bezug [kWh]:\t "+str(int(obis_wirkenergiebezug,16)/1000)
                print (wirkenergiebezug)


            # Wirkenergie Lieferung -A (Wh)
            # 0100020800ff

            obis_wirkenergielieferung = '0100020800ff'
            obis_wirkenergielieferung_pos = databin.find(obis_wirkenergielieferung)
            if obis_wirkenergielieferung_pos > 1:
                #print ("obis_wirkenergielieferung_pos: ", obis_wirkenergielieferung_pos)

                obis_wirkenergielieferung_anzzeichen = 8
                #print ("obis_wirkenergielieferung_anzzeichen: ", obis_wirkenergielieferung_anzzeichen)

                obis_wirkenergielieferung = databin[obis_wirkenergielieferung_pos+obis_len+2:obis_wirkenergielieferung_pos+obis_len+2+obis_wirkenergielieferung_anzzeichen]
                wirkenergielieferung = "1.0.2.8.0.255\tWirkenergie Lieferung [kWh]:\t "+str(int(obis_wirkenergielieferung,16)/1000)
                print (wirkenergielieferung)


            # Blindleistung Bezug +R (Wh)
            # 0100030800ff

            obis_blindleistungbezug = '0100030800ff'
            obis_blindleistungbezug_pos = databin.find(obis_blindleistungbezug)
            if obis_blindleistungbezug_pos > 1:
                #print ("obis_blindleistungbezug_pos: ", obis_blindleistungbezug_pos)

                obis_blindleistungbezug_anzzeichen = 8
                #print ("obis_blindleistungbezug_anzzeichen: ", obis_blindleistungbezug_anzzeichen)

                obis_blindleistungbezug = databin[obis_blindleistungbezug_pos+obis_len+2:obis_blindleistungbezug_pos+obis_len+2+obis_blindleistungbezug_anzzeichen]
                blindleistungbezug = "1.0.3.8.0.255\tBlindleistung Bezug [kW]:\t "+str(int(obis_blindleistungbezug,16)/1000)
                print (blindleistungbezug)



            # Blindleistung Lieferung -R (Wh)
            # 0100040800ff

            obis_blindleistunglieferung = '0100040800ff'
            obis_blindleistunglieferung_pos = databin.find(obis_blindleistunglieferung)
            if obis_blindleistunglieferung_pos > 1:
                #print ("obis_blindleistunglieferung_pos: ", obis_blindleistunglieferung_pos)

                obis_blindleistunglieferung_anzzeichen = 8
                #print ("obis_blindleistunglieferung_anzzeichen: ", obis_blindleistunglieferung_anzzeichen)

                obis_blindleistunglieferung = databin[obis_blindleistunglieferung_pos+obis_len+2:obis_blindleistunglieferung_pos+obis_len+2+obis_blindleistunglieferung_anzzeichen]
                blindleistunglieferung = "1.0.4.8.0.255\tBlindleistung Lieferung [kW]:\t "+str(int(obis_blindleistunglieferung,16)/1000)
                print (blindleistunglieferung)

            if logging > 0:
                logger = open(zaehlernummerfilename+".log", "a")
                logger.write("\n"+ueberschrift)
                logger.write("\n"+datum_zeit)
                logger.write("\n"+zaehlernummer)
                logger.write("\n"+cosemlogdevname)
                logger.write("\n"+spannungl1)
                logger.write("\n"+spannungl2)
                logger.write("\n"+spannungl3)
                logger.write("\n"+stroml1)
                logger.write("\n"+stroml2)
                logger.write("\n"+stroml3)
                logger.write("\n"+wirkleistungbezug)
                logger.write("\n"+wirkleistunglieferung)
                logger.write("\n"+wirkenergiebezug)
                logger.write("\n"+wirkenergielieferung)
                logger.write("\n"+blindleistungbezug)
                logger.write("\n"+blindleistunglieferung+"\n"+"\n")
                logger.close()

serial.close()




