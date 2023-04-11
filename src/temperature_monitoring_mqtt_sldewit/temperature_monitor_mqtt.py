"""Module providing temperature monitoring for multiple temperature sensors to MQTT"""
# pylint: disable=W0703
import sys
from threading import Thread, Event
import paho.mqtt.client as mqtt
from pi1wire import Pi1Wire

class TemperatureSensor:
    """Class representing a temperature sensor"""
    topic = ""
    temperature = 0.0
    sensorstate = "offline"
    sensoraddress = 0
    temperaturesensor = 0
    mqtt_broker = 0

    def __init__(self, topic, sensoraddress, mqtt_broker) -> None:
        """Init function"""
        self.topic = topic
        self.mqtt_broker = mqtt_broker
        self.sensoraddress = sensoraddress
        try:
            self.temperaturesensor = Pi1Wire().find(self.sensoraddress)
            self.sensorstate = "online"
        except Exception as pi1wire_exception:
            self.sensorstate = "not found"
            print(f"Exception initializing sensor: {pi1wire_exception}")

    def read(self):
        """Sensor read function"""
        if self.temperaturesensor != 0:
            try:
                self.temperature = round(self.temperaturesensor.get_temperature(),1)
                self.sensorstate = "online"
            except Exception as sensor_exception:
                self.sensorstate = "offline"
                print(f"Exception while reading sensor: {sensor_exception}")
        else: #simulate in case not really there
            self.temperature += 0.1
            print(f"Simulate sensor: {self.topic} - {self.temperature}")

    def publish(self):
        """Sensor publish to MQTT function"""
        sensor_value = f"{{\"temperatuur\":\"{self.temperature}\"}}"
        # pylint: disable-next=C0301
        sensor_attr = f"{{\"mac_address\":\"{self.sensoraddress}\",\"status\":\"{self.sensorstate}\"}}"
        print(f"Publish {self.topic} as {self.temperature}")
        try:
            self.mqtt_broker.publish(self.topic,
                                     payload = sensor_value,
                                     qos=0, retain=True)
            self.mqtt_broker.publish(self.topic+'/attributes',
                                     payload = sensor_attr,
                                     qos=0,
                                     retain=False)
        except Exception as mqtt_exception:
            print(f"MQTT publish failed on topic {self.topic} : {mqtt_exception}")

# pylint: disable-next=W0613
def on_connect(client, userdata, flags, return_code):
    """On connect event"""
    if return_code == 0:
        print("Connected success")
    else:
        print(f"Connected fail with code {return_code}")

class MyThread(Thread):
    """Class for time thread"""
    interval = 1
    def __init__(self, event, interval):
        """Init function"""
        Thread.__init__(self)
        self.stopped = event
        self.interval = interval

    def run(self):
        """Run function of timed thread"""
        while not self.stopped.wait(self.interval):
            for sensor in SENSORS:
                sensor.read()
                sensor.publish()

try:
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.will_set('vloerverwarming/status', "offline")
    mqtt_client.username_pw_set("mqtt","test_mqtt")
    mqtt_client.connect("192.168.2.209", 1883, 60)
    mqtt_client.publish('vloerverwarming/status',payload = "online", qos=0, retain=True)
    mqtt_client.publish('vloerverwarming/version/installed',payload = "1.0.0", qos=0, retain=True)
    mqtt_client.publish('vloerverwarming/version/latest',payload = "1.0.0", qos=0, retain=True)
    mqtt_client.loop_start()
except Exception as connect_exception:
    print(f"Failed to connect to MQTT: {connect_exception}")
    sys.exit()

SENSORS = []

SENSORS.append(TemperatureSensor('vloerverwarming/kring1/aanvoertemp',"28dfc6571f64ff",mqtt_client))
SENSORS.append(TemperatureSensor('vloerverwarming/kring1/afvoertemp',"28dfd9571f64ff",mqtt_client))
SENSORS.append(TemperatureSensor('vloerverwarming/kring2/aanvoertemp',"2828ff571f64ff",mqtt_client))
SENSORS.append(TemperatureSensor('vloerverwarming/kring2/afvoertemp',"28aafd571f64ff",mqtt_client))
SENSORS.append(TemperatureSensor('vloerverwarming/kring3/aanvoertemp',"28072261300627",mqtt_client))
SENSORS.append(TemperatureSensor('vloerverwarming/kring3/afvoertemp',"280722613294cc",mqtt_client))
SENSORS.append(TemperatureSensor('vloerverwarming/kring4/aanvoertemp',"280722614c7990",mqtt_client))
SENSORS.append(TemperatureSensor('vloerverwarming/kring4/afvoertemp',"280922545d1f8a",mqtt_client))
SENSORS.append(TemperatureSensor('vloerverwarming/aanvoertemp',"282bfe571f64ff",mqtt_client))
SENSORS.append(TemperatureSensor('vloerverwarming/afvoertemp',"28092254776424",mqtt_client))

stop_flag = Event()
thread= MyThread(stop_flag, 10)
thread.start()
