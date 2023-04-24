import json

class TemperatureSensor:
    """Class representing a temperature sensor"""
    topic = ""
    temperature = 0.0
    sensorstate = "offline"
    sensoraddress = ""
    temperaturesensor = 0
    mqtt_broker = "mqtt.Client()"
    sensor_value = {
        "temperatuur": "0.0"
    }
    sensor_attr = {
        "mac_address": "",
        "status": "offline"
    }

    def __init__(self, topic, sensoraddress, mqtt_broker) -> None:
        """Init function"""
        self.topic = topic
        self.mqtt_broker = mqtt_broker
        self.sensoraddress = sensoraddress
        self.sensor_attr["mac_address"] = sensoraddress
        self.sensor_attr["status"] = "online"

    def read(self,temperature):
        """test"""
        self.sensor_value["temperatuur"] = str(temperature)


    def publish(self):
        """test"""
        print(json.dumps(self.sensor_value, indent=4))
        print(json.dumps(self.sensor_attr, indent=4))



t1 = TemperatureSensor('vloerverwarming/kring1/aanvoertemp',"28dfc6571f64ff","mqtt_client")

t1.publish()

t1.read(3.0)

t1.publish()
