from simple import MQTTClient
import machine
import time
import sys
import micropython
from time import sleep
from machine import Pin
import gc
gc.collect()


mqtt_server = '1*0'
user = '*rca'
passw = 'Pa**2'
client_id = 'esp32sds'
#topic_uv = 'uv'
topic_t = 'dht22_temp'
topic_h = 'dht22_humi'
topic_sub = 'sleep'
#topic_ds = 'ds18'
sleep_time = int(1200000)                                 #time period staying in deep sleep

def deep_sleep(msecs):
  # configure RTC.ALARM0 to be able to wake the device
  rtc = machine.RTC()
  rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

  # set RTC.ALARM0 to fire after X milliseconds (waking the device)
  rtc.alarm(rtc.ALARM0, msecs)

  # put the device to sleep
  machine.deepsleep()

dht = machine.DHT(machine.Pin(14), machine.DHT.DHT2X)     #defining dht22 pin

def sub_cb(topic, msg):
  global sleep_time
  sleep_time = int(msg)
  if topic == b'status' and msg == b'connected':
    print('ESP received hello message')

def connect_and_subscribe():                              #function to connect to mqtt broker
  global client_id, mqtt_server, topic_sub
  client = MQTTClient(client_id, mqtt_server, user=user, password=passw)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  return client

def restart_and_reconnect():                              #function to reset the board
  machine.reset()
  
sleep(30) 
while True:
  try:
    client = connect_and_subscribe()
    sleep(10)
    while True:
      result, temperature, humidity = dht.read()          #Reading from dht22
      sleep(3)                                            #giving 3 seconds time to read the data
      print('t={} C'.format(temperature))
      print('h={} % RH'.format(int(humidity)))
      msg_temp = b'%3.1f' %temperature
      msg_humi = b'%3.1f' %humidity
      client.publish(topic_t, msg_temp)                   #publish dht temp
      client.publish(topic_h, msg_humi)                   #publish dht humi
      sleep(5)                                            #giving 5 seconds delay bofore going to deep sleep
      print('Going to deep sleep')                        
      print(sleep_time)
      machine.deepsleep(sleep_time)                       #deep sleep command
  except OSError as e:
    print('Failed to connect to MQTT broker. Trying to reconnect...')
    restart_and_reconnect()

