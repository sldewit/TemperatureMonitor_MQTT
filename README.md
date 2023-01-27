
# Temperature monitoring system using MQTT

[![Stable Release][stable_release]][stable_release]
[![Project Maintenance][maintenance-shield]][user_profile]
[![License][license-shield]](LICENSE)
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

Monitoring system several temperature sensors. One of the use cases is for a floor heating system with heat exchanger. 

This system is design to monitor several different loops in a floor heating system using a heat exchanger. The measured data is published to a MQTT broker. 

# Hardware setup

The system is built arround 1-wire temperature sensor DS18B20 connected to a Raspberry Pi with 1-wire setup as default on GPIO 4. 

My specific project will be using 10 DS18B20 sensors to monitor my total 8 loops + supply/return on the heat exchanger. They are connected as shown in this picture:

![Figure 1-1](https://github.com/sldewit/TemperatureMonitor_MQTT/blob/5161e3ec3d567c0ba0c02cbbaa3b987bfebc9c35/Fritzing/Vloerverwarming%20monitor_schema.svg)

My POC setup for now uses only 5 DS18B20 sensors. 

Below my basic call structure for 5 different sensors.

```
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
```

[buymecoffee]: https://www.buymeacoffee.com/sldewit
[buymecoffeebadge]: https://www.buymeacoffee.com/assets/img/custom_images/yellow_img.png
[license-shield]: https://img.shields.io/github/license/sldewit/TemperatureMonitor_MQTT.svg
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40sldewit-blue.svg
[user_profile]: https://github.com/sldewit
[stable_release]: https://shields.io/github/v/release/sldewit/TemperatureMonitor_MQTT?label=stable&sort=semver
