#!/usr/bin/env python3

from paho.mqtt import client as mqtt
from time import sleep

broker = '192.168.15.148'

def on_message(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)

client = mqtt.Client("L1")
client.on_message=on_message
client.connect(broker)
client.loop_start()
try:
    client.subscribe("sensors/#")
    while True:
        sleep(1)
finally:
    client.loop_stop()
