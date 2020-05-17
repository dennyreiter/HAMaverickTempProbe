#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import subprocess
import sys
import time
import paho.mqtt.client as mqtt
import os
import json

from config import *

# 915MHz
# rtl_433_cmd = "/usr/local/bin/rtl_433 -f 915M -F json" 
# Maverick Temp probe
rtl_433_cmd = "/usr/local/bin/rtl_433 -f 433.776m -F json" 
#rtl_433_cmd = "/usr/local/bin/rtl_433 -F json" 

# Define MQTT event callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")

def on_message(client, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def on_publish(client, obj, mid):
    print("mid: " + str(mid))

def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(client, obj, level, string):
    print(string)

# Setup MQTT connection

mqttc = mqtt.Client()
# Assign event callbacks
#mqttc.on_message = on_message
mqttc.on_connect = on_connect
#mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
mqttc.on_disconnect = on_disconnect

# Uncomment to enable debug messages
#mqttc.on_log = on_log

# Uncomment the next line if your MQTT server requires authentication
#mqttc.username_pw_set(MQTT_USER, password=MQTT_PASS)
mqttc.connect(MQTT_HOST, MQTT_PORT, 60)

mqttc.loop_start()

# Start RTL433 listener
rtl433_proc = subprocess.Popen(rtl_433_cmd.split(),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True)


while True:
    for line in iter(rtl433_proc.stdout.readline, '\n'):
        print(line)
        if "time" in line:
            subtopic = ""
            json_dict = json.loads(line)
            for item in json_dict:
                value = json_dict[item]
                if "model" in item:
                    subtopic+="/"+value
            for item in json_dict:
                value = json_dict[item]
                if "id" in item:
                    subtopic+="/"+str(value)

            mqttc.publish(MQTT_TOPIC+subtopic+"/STATE", payload=line,qos=MQTT_QOS)

