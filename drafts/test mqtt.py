import paho.mqtt.client as mqtt
from threading import Thread, Event
from pi1wire import Pi1Wire, Resolution

class MyThread(Thread):
    interval = 1
    def __init__(self, event, interval):
        Thread.__init__(self)
        self.stopped = event
        self.interval = interval

    def run(self):
        while not self.stopped.wait(self.interval):
            Read_Temperature()
            Send_Temperature()
            
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected success")
    else:
        print(f"Connected fail with code {rc}")

def Read_Temperature():
    global Kring1_AanvoerTemp, Kring1_AfvoerTemp
    global Kring2_AanvoerTemp, Kring2_AfvoerTemp
    global AanvoerTemp
    try:
        Kring1_AanvoerTemp = TempSensor1.get_temperature()
    except:
        print("T1 not found")
    try:
        Kring1_AfvoerTemp = TempSensor2.get_temperature()
    except:
        print("T2 not found")
    print(f'{Kring1_AanvoerTemp:.3f} - {Kring1_AfvoerTemp:.3f}')
    try:
        Kring2_AanvoerTemp = TempSensor3.get_temperature()
    except:
        print("T3 not found")
    try:
        Kring2_AfvoerTemp = TempSensor4.get_temperature()
    except:
        print("T4 not found")
    print(f'{Kring2_AanvoerTemp:.3f} - {Kring2_AfvoerTemp:.3f}')
    try:
        AanvoerTemp = TempSensor5.get_temperature()
    except:
        print("T5 not found")
    print(f'{AanvoerTemp:.3f}')
    

def Send_Temperature():
    client.publish('verwarming/kring1/aanvoertemp',payload = '{"temperatuur":"%.1f"}' %Kring1_AanvoerTemp, qos=0, retain=True)
    print('{"Aanvoer temperatuur":"%.1f"}' %Kring1_AanvoerTemp)
    client.publish('verwarming/kring1/afvoertemp',payload = '{"temperatuur":"%.1f"}' %Kring1_AfvoerTemp, qos=0, retain=True)
    print('{"Afvoer temperatuur":"%.1f"}' %Kring1_AfvoerTemp)
    client.publish('verwarming/kring2/aanvoertemp',payload = '{"temperatuur":"%.1f"}' %Kring2_AanvoerTemp, qos=0, retain=True)
    print('{"Aanvoer temperatuur":"%.1f"}' %Kring2_AanvoerTemp)
    client.publish('verwarming/kring2/afvoertemp',payload = '{"temperatuur":"%.1f"}' %Kring2_AfvoerTemp, qos=0, retain=True)
    print('{"Afvoer temperatuur":"%.1f"}' %Kring2_AfvoerTemp)
    client.publish('verwarming/aanvoertemp',payload = '{"temperatuur":"%.1f"}' %AanvoerTemp, qos=0, retain=True)
    print('{"Aanvoer temperatuur":"%.1f"}' %AanvoerTemp)

#init 1-wire sensors
try:
    TempSensor1 = Pi1Wire().find("28dfc6571f64ff")
except Exception as e:
    print("T1 not found")
    print(e)
Kring1_AanvoerTemp = 0.0

try:
    TempSensor2 = Pi1Wire().find("28dfd9571f64ff")
except:
    print("T2 not found")
Kring1_AfvoerTemp = 0.0

try:
    TempSensor3 = Pi1Wire().find("2828ff571f64ff")
except:
    print("T3 not found")
Kring2_AanvoerTemp = 0.0

try:
    TempSensor4 = Pi1Wire().find("28aafd571f64ff")
except:
    print("T4 not found")
Kring2_AfvoerTemp = 0.0

try:   
    TempSensor5 = Pi1Wire().find("282bfe571f64ff")
except:
    print("T5 not found")
AanvoerTemp = 0.0

client = mqtt.Client() 
client.on_connect = on_connect
client.will_set('raspberry/status', b'{"status": "Off"}')
client.username_pw_set("mqtt","test_mqtt")
client.connect("ha.de-wit.me", 1883, 60)
client.publish('raspberry/status',payload = '{"status": "On"}', qos=0, retain=True)
client.loop_start()

stopFlag = Event()
thread= MyThread(stopFlag, 10)
thread.start()
