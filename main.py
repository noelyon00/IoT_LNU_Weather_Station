from machine import ADC, Pin, I2C

from network import WLAN      # For operation of WiFi network
import time                   # Allows use of time.sleep() for delays
import pycom                  # Base library for Pycom devices
from mqtt import MQTTClient  # For use of MQTT protocol to talk to Adafruit IO
import ubinascii              # Needed to run any MicroPython code
import machine                # Interfaces with hardware components
import micropython            # Needed to run any MicroPython code
import ssd1306                # Library for the OLED onn the dev-board

from dht import DHT


# BEGIN SETTINGS
# These need to be change to suit your environment
READINGS_INTERVAL = 20000 # milliseconds

# Wireless network credentials
WIFI_SSID = "COMHEM_3679f9"
WIFI_PASS = "rzmjhtiz" # No this is not our regular password. :)

# Adafruit IO (AIO) configuration and credentials
AIO_SERVER = "io.adafruit.com"
AIO_PORT = 1883
AIO_USER = "Nojoshima"
AIO_KEY = "aio_wzqN444BQHNklSGPRAvKygoVFI8x"
AIO_CLIENT_ID = ubinascii.hexlify(machine.unique_id())  # Can be anything
AIO_CONTROL_FEED = "Nojoshima/feeds/lights"
AIO_TEMP_FEED = "Nojoshima/feeds/temperature"
AIO_HUMID_FEED = "Nojoshima/feeds/humidity"


# Start OLED
oled_width = 128
oled_height = 64
#OLED reset pin
i2c_rst = Pin('P16', mode=Pin.OUT)
# Initialize the OLED display
i2c_rst.value(0)
time.sleep_ms(5)
i2c_rst.value(1) # must be held high after initialization
time.sleep_ms(500)
# Setup the I2C pins
i2c_scl = Pin('P4', mode=Pin.OUT, pull=Pin.PULL_UP)
i2c_sda = Pin('P3', mode=Pin.OUT, pull=Pin.PULL_UP)
i2c = I2C(0, I2C.MASTER, baudrate=100000, pins=(i2c_sda,i2c_scl))
time.sleep_ms(500)
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
oled.fill(0)
oled.text('Booting up...', 0, 20)
oled.show()
time.sleep(1)
oled.text('Connecting to WiFi...', 0, 40)
oled.show()

# WIFI protocol
# We need to have a connection to WiFi for Internet access
wlan = WLAN(mode=WLAN.STA)
wlan.connect(WIFI_SSID, auth=(WLAN.WPA2, WIFI_PASS))

while not wlan.isconnected():    # Code waits here until WiFi connects
    machine.idle()

# Display shows WiFi connection success and device IP
print("Connected to Wifi")
oled.fill(0)
oled.text(wlan.ifconfig()[0], 0, 0)
oled.text('WiFi connected', 0, 25)
oled.text('Transmitting...', 0, 55)
oled.show()


# FUNCTIONS
def reading():

    th = DHT(Pin('P19', mode=Pin.OPEN_DRAIN), 0)
    temp = 15 + (machine.rng() % 50)/10
    humid = 20 + (machine.rng() % 400)/10
    # With a functioning sensor uncomment this snippet below
    """result = th.read()
    while not result.is_valid():
        print("No data")
        time.sleep(.5)
        result = th.read()
    temp = result.temperature
    humid = result.humidity
    print('Temp:', result.temperature)
    print('RH:', result.humidity)"""
    time.sleep(2)
    return [temp, humid]


def send_readings():
    global READINGS_INTERVAL

    if (time.ticks_ms() < READINGS_INTERVAL):
        return; # Too soon since last one sent.

    readings = reading()
    print("Publishing: {0} to {1} ... ".format(str(readings), "Adafruit feeds"), end='')
    try:
        client.publish(topic=AIO_TEMP_FEED, msg=str(readings[0]))
        client.publish(topic=AIO_HUMID_FEED, msg=str(readings[1]))
        print("DONE")
        oled.fill(0)
        oled.text("Temp: " + str(readings[0]) + " C", 0, 20)
        oled.text("Humidity: " + str(readings[1]) + " %", 0, 40)
        oled.show()
    except Exception as e:
        print("FAILED")
    finally:
        last_random_sent_ticks = time.ticks_ms()


# Use the MQTT protocol to connect to Adafruit IO
client = MQTTClient(AIO_CLIENT_ID, AIO_SERVER, AIO_PORT, AIO_USER, AIO_KEY)
client.connect()

try:                      # Code between try: and finally: may cause an error
                          # so ensure the client disconnects the server if
                          # that happens.
    while 1:              # Repeat this loop forever
        client.check_msg()# Action a message if one is received. Non-blocking.
        send_readings()     # Send readings to Adafruit IO if it's time.
finally:                  # If an exception is thrown ...
    client.disconnect()   # ... disconnect the client and clean up.
    client = None
    wlan.disconnect()
    wlan = None
    print("Disconnected from Adafruit IO.")
