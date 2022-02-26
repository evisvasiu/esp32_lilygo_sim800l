

from simple import MQTTClient
import machine
import time
import sys
import micropython
from time import sleep
from machine import Pin
import gc
gc.collect()


mqtt_server = '13***0'
user = 'jezerca'
passw = 'Password@2'
client_id = 'esp32sds'
#topic_uv = 'uv'
topic_t = 'dht**mp'
topic_h = 'd**i'
topic_sub = 's***'
#topic_ds = 'ds18'
sleep_time = int(1200000)
def deep_sleep(msecs):
  # configure RTC.ALARM0 to be able to wake the device
  rtc = machine.RTC()
  rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

  # set RTC.ALARM0 to fire after X milliseconds (waking the device)
  rtc.alarm(rtc.ALARM0, msecs)

  # put the device to sleep
  machine.deepsleep()

dht = machine.DHT(machine.Pin(14), machine.DHT.DHT2X)

def sub_cb(topic, msg):
  global sleep_time
  sleep_time = int(msg)
  if topic == b'notification' and msg == b'received':
    print('ESP received hello message')

def connect_and_subscribe():
  global client_id, mqtt_server, topic_sub
  client = MQTTClient(client_id, mqtt_server, user=user, password=passw)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  machine.reset()
  
sleep(30) 
while True:
  try:
    client = connect_and_subscribe()
    sleep(10)
    while True:
      result, temperature, humidity = dht.read()
      print('t={} C'.format(temperature))
      msg_temp = b'%3.1f' %temperature
      msg_humi = b'%3.1f' %humidity
      sleep(2)
      client.publish(topic_t, msg_temp)
      client.publish(topic_h, msg_humi)      #publish dht temp
      sleep(5)
      print('Going to deep sleep')                #deep sleep command
      print(sleep_time)
      machine.deepsleep(sleep_time)
  except OSError as e:
    print('Failed to read sensor. Reconnecing...')
    restart_and_reconnect()


