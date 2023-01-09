import paho.mqtt.client as mqtt
from threading import Thread, Event
from pi1wire import Pi1Wire, Resolution

class TemperatureSensor:
    topic = ""
    temperature = 0.0
    sensorstate = "offline"
    sensoraddress = 0
    temperaturesensor = 0
    MQTT_Broker = 0

    def __init__(self, topic, sensoraddress, mqtt_broker) -> None:
        self.topic = topic
        self.MQTT_Broker = mqtt_broker
        self.sensoraddress = sensoraddress
        try:
            self.temperaturesensor = Pi1Wire().find(self.sensoraddress)
            self.sensorstate = "online"
        except Exception as e:
            self.sensorstate = "not found"
            print(f"Exception initializing sensor: {e}")    

    def read(self):
        if self.temperaturesensor != 0:
            try:
                self.temperature = self.temperaturesensor.get_temperature()
                self.sensorstate = "online"
            except Exception as e:
                self.sensorstate = "offline"
                print(f"Exception while reading sensor: {e}")  
        else: #simulate in case not really there
            self.temperature += 0.1            
            print(f"Simulate sensor: {self.topic} - {self.temperature}")

    def publish(self):
        try:
            self.MQTT_Broker.publish(self.topic,payload = '{"temperatuur":"%.1f"}'%self.temperature , qos=0, retain=True)
            self.MQTT_Broker.publish(self.topic+'/attributes', payload = '{"mac_address":"'+self.sensoraddress+'","status":"'+self.sensorstate+'"}', qos=0, retain=False)
        except Exception as e:
            print(f"MQTT publish failed: {e}")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected success")
    else:
        print(f"Connected fail with code {rc}")

class MyThread(Thread):
    interval = 1
    def __init__(self, event, interval):
        Thread.__init__(self)
        self.stopped = event
        self.interval = interval

    def run(self):
        global Sensors
        while not self.stopped.wait(self.interval):
            for sensor in Sensors:
                sensor.read()
                sensor.publish()

try:
    client = mqtt.Client() 
    client.on_connect = on_connect
    client.will_set('vloerverwarming/status', "offline")
    client.username_pw_set("mqtt","test_mqtt")
    client.connect("ha.de-wit.me", 1883, 60)
    client.publish('vloerverwarming/status',payload = "online", qos=0, retain=True)
    client.publish('vloerverwarming/version/installed',payload = "1.0.0", qos=0, retain=True)
    client.publish('vloerverwarming/version/latest',payload = "1.0.0", qos=0, retain=True)
    client.loop_start()
except Exception as e:
    print(f"Failed to connect to MQTT: {e}")
    exit()

Sensors = []

Sensors.append(TemperatureSensor('vloerverwarming/kring1/aanvoertemp',"28dfc6571f64ff",client))
Sensors.append(TemperatureSensor('vloerverwarming/kring1/afvoertemp',"28dfd9571f64ff",client))
Sensors.append(TemperatureSensor('vloerverwarming/kring2/aanvoertemp',"2828ff571f64ff",client))
Sensors.append(TemperatureSensor('vloerverwarming/kring2/afvoertemp',"28aafd571f64ff",client))
Sensors.append(TemperatureSensor('vloerverwarming/aanvoertemp',"282bfe571f64ff",client))

stopFlag = Event()
thread= MyThread(stopFlag, 10)
thread.start()
