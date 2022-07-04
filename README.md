# In-house weather station powered by IoT

## Author
Noel Efrem(ne222md) at Linnaeus University


## Overview

### Short project description
The goal of this project is build an IoT device capable of measuring the temperature and humidity of a regular room. The data will be sent over to a IoT cloud platform where it is possible to visualise and trigger notifications.

### Objective
The motivation behind this project was a medical purpose. I am quite sensitive to low humidity (cause by regular ventilation) as it can lead allergic reactions and usually resolve by opening the window. However, during extreme seasons the cost of fixing humidity comes with the cost of messing up the room temperature which is why this IoT device is perfect for my condition.

**NOTE!** A week before finalising this project I was having trouble getting readings from my dev-board. After thorough  troubleshooting of changing sensors, cables, flashing with Arduino instead of micropython and even discussion with other students with the same or similar project I came to the conclusion that my dev-board is faulty. This is the only component I did not replace and did not have time to do so before this report. Upon discussing this with a teacher, Fredrik, it was suggested that I document everything as it were working. I came up with a way to simulate the data so everything in this project is done as if I had correct readings. The code I use to read from my sensor is commented out but it is proven to work before and its place is a simulation using random but reasonable numbers

### Approximated project completion time

Around 1-2 hours. This is an estimate assuming there are no faulty components.

## Hardware components
The materials used can be found in the table below:

| Item | Price | Specs  |
| ------------- | ------------- | ------------- |
| [Heltec ESP32][Hel]  | 370 kr  | A powerful OLED equipped dev-board <br />with built-in WiFi and LoRa capabilities. |
| [Digital temperature and <br /> humidity sensor DHT11][DHT]  | 39.20 kr  | Digital temperature and humidity <br/> sensor  |
| [Breadboard 2 pack][bread]  | 99.90 kr  | Breadboard with 400 connection points  |
| [Jumper wires male-female][wires]  | 23.20 kr  | Wires to make connections between <br /> the various components |

## Computer Setup
### Prerequisites
* Python 2.7 or higher
* Pip, installer for python modules. Follow this [guide][pip]
* Esptool, firmware installer. Install in CMD using ``` pip install esptool```
* Atom, a user-friendly IDE.
* Hardware drive, for the Heltec board use this [link][hardware]

### Flashing
**Step 1: Install board driver**<br />
Install the driver using [this][driver]. Go to Device Managers and find your driver's serial port. It should of the format COMX.

**Step 2: Flashing with Micropython**<br />
First, the files in the board have to be erased. This can be done in CMD using ```esptool.py --port COMX erase_flash```. Download [this zip file][heltecbin] and extract the bin file somewhere. Flash the board using the following command ```esptool.py --chip esp32 --port COMX write_flash -z 0x1000 X:\somewhere\Heltec.bin``` where COMX is to be replaced with the correct port nr.

**Step 3: Success?**<br />
The board has a built-in compiler. To test if flashing is successful type this ```print("Hello World")``` in the terminal and the output should be Hello World.

### Uploading code to the dev-board
**Step 1: Create a project and files**<br />
Create a project in Atom going to ```File > Add Project Folder``` and create a folder called **Library**, in which to store external libraries for the sensors/devices if needed, and create a python file **main.py** in which all the coding will be written.

**Step 2: Upload the project to the dev-board**<br />
![image](https://gits-15.sys.kth.se/storage/user/18917/files/a7a3e1c0-e86b-4146-92f5-fb7bd4224276)
As can be seen in the picture, connect to your device by choosing the correct serial port COMX. Select the project and press upload to upload the files to the device. If successful, main file should compile right away.


## Putting everything together



![image](https://gits-15.sys.kth.se/storage/user/18917/files/08479860-aae8-4fd6-81b1-46396f048300)



The DHT11 sensor used is three pin version (power, data, ground) and it is connected to the Heltec dev-board using a breadboard. Wire as shown in the picture. This is different from the provided schematics in the website where it is bought from which are incorrect. Make sure to plug in the micro-USB after you are done and confident with the wiring to avoid frying the sensors.


## Platform

The chosen platform for this project is Adafruit IO, an IoT cloud platform. It uses MQTT as the communication protocol. The free version is used and is limited in points per minute, data storage duration and more features for the visualisation dashboard. However, for this development project the free version will suffice.

In the future, it would be good to consider using the paid subsricption for the sole purpose of having unthrottled notification capabilities. The more updated I am, the faster I can counteract change in conditions.

## The code

The functional code snippets will can be found here below. For the full code including the simulation for the readings, visit this [link][maincode]

The function that reads that the data from the sensor is as follows:
```
def reading():

    th = DHT(Pin('P19', mode=Pin.OPEN_DRAIN), 0)
    result = th.read()
    while not result.is_valid():
        print("No data")
        time.sleep(.5)
        result = th.read()
    temp = result.temperature
    humid = result.humidity
    time.sleep(2)
    return [temp, humid]
```
The function that transmits readings but also updates the display with the readings is as follows:
```
def send_readings():
    global READINGS_INTERVAL

    if ((time.ticks_ms() - last_random_sent_ticks) < READINGS_INTERVAL):
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
```

## Transmitting the data / connectivity

The readings are sent using a chosen communication protocol to an IoT platform every 20 seconds.

For this data transmission the WiFi communication protocol is used as my device will be a stationary device plugged to a power supply. As WiFi uses more power than LoRa due to internet connectivity, it won't be an issue in this case since a power supply is used instead of a battery. WiFi is also not so good when it comes to low range, however, as in this case, it is perfectly suitable for in household application.

The transport protocol used is the one support by Adafruit IO, which is the MQTT protocol. It is perfect for smaller IoT devices as it is very reliable in delivering the data and is also battery friendly.

## Presenting the data
![image](https://gits-15.sys.kth.se/storage/user/18917/files/08b775a0-4a27-4c19-b1cb-535448f8a5b7)

Adafruit IO has it own visualisation dashoard which was used in this project. The data is being saved every time data is being sent, which is every 20 seconds. This is well below the limit of the free version of Adafruit IO. It is possible to send up to 30 data points per minute but I am currently only sending 6 data points per minute. This can be seen in the histroy chart in the above picture.

![image](https://gits-15.sys.kth.se/storage/user/18917/files/ffd8c0e6-1fe1-46e1-862f-04d2b2bded40)

Adafruit IO has also an action center from where the data can be used to trigger alerts and notification. I have used Discord webhooks in an IoT devices dedicated channel for myself. Discord is a great platform for me as a student to constantly uses it to get notified on. <br />
![image](https://gits-15.sys.kth.se/storage/user/18917/files/3596f7ad-b9c1-4e4a-8e02-fbe163c822d8)

## Finalising the design
![20220704_174241](https://gits-15.sys.kth.se/storage/user/18917/files/dec80644-b9c7-451f-827e-0f017b427772)

The reiterate the goal of this project, it was for me or anyone else sensitive to weather and humidity conditions to have the data needed to avoid getting sick. I feel like I have managed to fullfil my goal with my project.

As this is something that is health related, it is crucial to have accurate sensors, therefore, an improvement to be made to this project is to use a more reliable sensor than the DHT11 that was used for this project. The DHT11 is a cheap sensor mainly used for development purposes and doesn't have the accuracies needed to be used when concerning health issues.

Adding more functionality such as an air quality sensor is something that would improve my project. As it is relevant to my allergy issues, it would be a suitable addition to my project.

The outcome of this project was as planned disregarding from the huge fact that the dev-board started to malfunction. The important part was that the majority of this project which is the essence of IoT could be done without the readings or just simulated readings. The code snippet for the data reading is present and upon receiving a new functioning board I have no doubt that I will have the data I need to sleep without a running nose or allergic reactions.



[Hel]: https://www.amazon.se/AZDelivery-NodeMCU-Heltec-OLED-sk%C3%A4rm-inklusive/dp/B08243JHMW/ref=mp_s_a_1_2?crid=1S6TWCYVJXKHX&keywords=heltec+esp32&qid=1654661719&sprefix=heltec%2Caps%2C96&sr=8-2&language=en_GB
[hardware]: https://www.silabs.com/documents/public/software/CP210x_Windows_Drivers.zip
[DHT]: electrokit.com/en/product/digital-temperature-and-humidity-sensor-dht11/
[wires]: https://www.electrokit.com/produkt/labbsladd-20-pin-15cm-hona-hane/
[pip]: https://pip.pypa.io/en/stable/installation/
[heltecbin]: https://github.com/H-Ryan/Heltec/blob/main/PyCom%20MicroPython/Heltec%20PyCom%20MicroPython.zip?raw=true
[driver]:https://www.silabs.com/documents/public/software/CP210x_Windows_Drivers.zip
[bread]:https://www.kjell.com/se/produkter/el-verktyg/elektronik/elektroniklabb/luxorparts-kopplingsdack-400-anslutningar-2-pack-p36283
[maincode]:https://github.com/noelyon00/IoT_LNU_Weather_Station/blob/690cc32ed9df611065fb0e7a0ce9c8aa824fd8cd/main.py
