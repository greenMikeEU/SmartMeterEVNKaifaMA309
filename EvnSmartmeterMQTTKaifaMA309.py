# Improved by Tobias Ecker OE3TEC 10/2022
from gurux_dlms.GXByteBuffer import GXByteBuffer
import serial
import time
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from binascii import unhexlify
import sys
import string
import paho.mqtt.client as mqtt
from gurux_dlms.GXDLMSTranslator import GXDLMSTranslator
from gurux_dlms.GXDLMSTranslatorMessage import GXDLMSTranslatorMessage
from bs4 import BeautifulSoup

# EVN Schlüssel eingeben zB. "36C66639E48A8CA4D6BC8B282A793BBB"
evn_schluessel = "8654A50B407E6AD35144828293DDBF1F"

#MQTT Verwenden (True | False)
useMQTT = False

#MQTT Broker IP adresse Eingeben ohne Port!
mqttBroker = "192.168.1.10"
mqttuser =""
mqttpasswort = ""
#Aktuelle Werte auf Console ausgeben (True | False)
printValue = True

#Comport Config/Init
comport = "/dev/ttyUSB0"


#MQTT Init
if useMQTT:
    try:
        client = mqtt.Client("SmartMeter")
        client.username_pw_set(mqttuser, mqttpasswort)
        client.connect(mqttBroker, port=1883)
    except:
        print("Die Ip Adresse des Brokers ist falsch!")
        sys.exit()



tr = GXDLMSTranslator()
tr.blockCipherKey = GXByteBuffer(evn_schluessel)
tr.comments = True
# MBUS ist fast immer 2400 Baud mit gerader Parität!
ser = serial.Serial( port=comport,
         baudrate=2400,
         bytesize=serial.EIGHTBITS,
         parity=serial.PARITY_EVEN,
         timeout=30, exclusive=True
)

def decode(daten_, tr_):
    msg = GXDLMSTranslatorMessage()
    msg.message = GXByteBuffer(daten_)
    xml = ""
    pdu = GXByteBuffer()
    tr_.completePdu = True
    while tr.findNextFrame(msg, pdu):
        pdu.clear()
        xml += tr_.messageToXml(msg)
    #print(len(xml))
    #print(pdu)
    
    if (len(xml) < 2900):
    	return 1
    
    soup = BeautifulSoup(xml, 'lxml')

    results_32 = soup.find_all('uint32')
    results_16 = soup.find_all('uint16')
    
    # https://programmerah.com/python-error-valueerror-invalid-literal-for-int-with-base-16-39529/
    str_results_32 = str(results_32)
    str_results_16 = str(results_16)
    w_p = str_results_32[16:16+8]
    w_n = str_results_32[52:52+8]
    m_p = str_results_32[88:88+8]
    m_n = str_results_32[124:124+8]
    ul1 = str_results_16[16:20]
    ul2 = str_results_16[48:52]
    ul3 = str_results_16[80:84]
    il1 = str_results_16[112:116]
    il2 = str_results_16[144:148]
    il3 = str_results_16[176:180]
    cos_phi = str_results_16[208:212]

    #Wirkenergie A+ in Wattstunden
    WirkenergieP = int(w_p,16)
    #Wirkenergie A- in Wattstunden
    WirkenergieN = int(w_n,16)
    #Momentanleistung P+ in Watt
    MomentanleistungP = int(m_p,16)
    #Momentanleistung P- in Watt
    MomentanleistungN = int(m_n,16)
    #Spannung L1 in Volt
    SpannungL1 = int(ul1,16)/10
    #Spannung L2 in Volt
    SpannungL2 = int(ul2,16)/10
    #Spannung L3 in Volt
    SpannungL3 = int(ul3,16)/10
    #Strom L1 in Ampere
    StromL1 = int(il1,16)/100
    #Strom L2 in Ampere
    StromL2 = int(il2,16)/100
    #Strom L3 in Ampere
    StromL3 = int(il3,16)/100
    #Leistungsfaktor
    Leistungsfaktor = int(cos_phi,16)/1000



    if printValue:
        print('Wirkenergie+: ' + str(WirkenergieP))
        print('Wirkenergie: ' + str(WirkenergieN))
        print('MomentanleistungP+: ' + str(MomentanleistungP))
        print('MomentanleistungP-: ' + str(MomentanleistungN))
        print('Spannung L1: ' + str(SpannungL1))
        print('Spannung L2: ' + str(SpannungL2))
        print('Spannung L3: ' + str(SpannungL3))
        print('Strom L1: ' + str(StromL1))
        print('Strom L2: ' + str(StromL2))
        print('Strom L3: ' + str(StromL3))
        print('Leistungsfaktor: ' + str(Leistungsfaktor))
        print('Momentanleistung: ' + str(MomentanleistungP-MomentanleistungN))
        print()
        print()


    #MQTT
    if useMQTT:
        connected = False
        while not connected:
            try:
                client.reconnect()
                connected = True
            except:
                print("Lost Connection to MQTT...Trying to reconnect in 2 Seconds")
                time.sleep(2)

        client.publish("Smartmeter/WirkenergieP", WirkenergieP)
        client.publish("Smartmeter/WirkenergieN", WirkenergieN)
        client.publish("Smartmeter/MomentanleistungP", MomentanleistungP)
        client.publish("Smartmeter/MomentanleistungN", MomentanleistungN)
        client.publish("Smartmeter/Momentanleistung", MomentanleistungP - MomentanleistungN)
        client.publish("Smartmeter/SpannungL1", SpannungL1)
        client.publish("Smartmeter/SpannungL2", SpannungL2)
        client.publish("Smartmeter/SpannungL3", SpannungL3)
        client.publish("Smartmeter/StromL1", StromL1)
        client.publish("Smartmeter/StromL2", StromL2)
        client.publish("Smartmeter/StromL3", StromL3)
        client.publish("Smartmeter/Leistungsfaktor", Leistungsfaktor)

while 1:
    daten = ser.read(size=282).hex()
    print(daten[0:8])
    
    if (len(daten) > 4):
    	if (daten[0:8] == "68fafa68"):
    		print("Jawohl!")
    		if decode(daten, tr) == 1:
    			print("No measurements in package or wrong key!")
    	else:
    		#Synchronisation
    		#Search for the longer pause between the messages
    		#Will be terminated if there is no data for 2 seconds
    		last_ok = 0
    		while ((ser.in_waiting > 0) or (last_ok < 2)):
    			print("Nix gut!")
    			while (ser.in_waiting > 0):
    				ser.read()
    			time.sleep(1)
    			if (ser.in_waiting == 0):
    				last_ok = last_ok + 1
    			else:
    				last_ok = 0


