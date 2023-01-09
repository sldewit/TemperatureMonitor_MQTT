======================
VloerverwarmingMonitor
======================

Monitor systeem voor vloerverwarming

Dit systeem is ontworpen om de verschillende kringen in een vloerverwarmings systeem te monitoren en te publiceren naar een MQTT broker.

.. code-block:: python

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

