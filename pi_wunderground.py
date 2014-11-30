#!/usr/bin/python

import subprocess
import re
import sys
import time
from datetime import datetime
import httplib
import urllib
import Adafruit_DHT

# ===========================================================
# Configuration options
# ===========================================================

# Type of sensor, can be Adafruit_DHT.DHT11, Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
DHT_TYPE = Adafruit_DHT.DHT22
DHT_PIN  = 6

# Time between posting readings to wunderground
delay = 600

# Wunderground personal weather station ID/password
stationid = "your_stationid"
password = "your_password"

# Loop to continously upload data (with delay)
while(True):

        # Attempt to get sensor reading.
        humidity, temp = Adafruit_DHT.read(DHT_TYPE, DHT_PIN)

        # Skip to the next reading if a valid measurement couldn't be taken.
        # This might happen if the CPU is under a lot of load and the sensor
        # can't be reliably read (timing is critical to read the sensor).
        if humidity is None or temp is None:
                time.sleep(2)
                continue

        tempf = (temp * 1.8) + 32

        print 'Temperature: {0:0.1f} C'.format(temp)
        print 'Temperature: {0:0.1f} F'.format(tempf)
        print 'Humidity:    {0:0.1f} %'.format(humidity)

        # upload data to Wunderground
        try:
                qs = {"ID": stationid, "PASSWORD": password, "dateutc": str(datetime.utcnow()), "tempf": tempf, "humidity": humidity, "softwaretype": "RaspberryPi", "action": "updateraw"}
                conn = httplib.HTTPConnection("weatherstation.wunderground.com")
                path = "/weatherstation/updateweatherstation.php?"+ urllib.urlencode(qs)
                conn.request("GET", path)
                res = conn.getresponse()

                # checks whether there was a successful connection (HTTP code 200 and content of page contains "success")
                if (int(res.status) == 200):
                        print "Next upload in %i seconds. Response: %s" % (delay, res.read())
                else:
                        print "%s -- Upload not successful, check username, password, and formating. Will try again in %i seconds" % (str(datetime.now()), delay)

        except IOError as e: #in case of any kind of socket error
                print "{0} -- I/O error({1}): {2} will try again in {3} seconds".format(datetime.now(), e.errno, e.strerror, delay)


        # Wait before re-uploading data
        time.sleep(delay)
