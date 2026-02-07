from geopy.geocoders import ArcGIS
from geopy.distance import distance
from routingpy.routers import OSRM
from configparser import ConfigParser
from time import time
from copy import copy
import sondehub

# Set up config parser, locator, and router
config = ConfigParser()
locator = ArcGIS()
router = OSRM(base_url='https://routing.openstreetmap.de/routed-car')

# Read in configuration
config.read('config.ini')

# Get address
addr = config['Location']['Address']
homeLoc = locator.geocode(addr)

# Tracking parameters
checkInterval = 600
sondeTimeout = 1800

# Initialize list of sondes
trackedSondes = {}

# Sonde check function
def sondeCheck(message):
    serials = trackedSondes.copy().keys()
    if message['serial'] not in serials:
        trackedSondes[message['serial']] = message
        trackedSondes[message['serial']]['lastSeen'] = time()
        trackedSondes[message['serial']]['lastChecked'] = 0
    else:
        trackedSondes[message['serial']]['lastSeen'] = time()

# Set up sonde stream
stream = sondehub.Stream(on_message=sondeCheck)

while True:
    serials = trackedSondes.copy().keys()
    for sonde in serials:
        if time() - trackedSondes[sonde]['lastSeen'] >= sondeTimeout:
            trackedSondes.pop(sonde)
        elif time() - trackedSondes[sonde]['lastChecked'] >= checkInterval:
            trackedSondes[sonde]['lastChecked'] = time()
            sondeLoc = locator.reverse([trackedSondes[sonde]['lat'], trackedSondes[sonde]['lon']])
            dist = distance(homeLoc.point, [trackedSondes[sonde]['lat'], trackedSondes[sonde]['lon']]).miles
            dirs = router.directions([homeLoc.point[1::-1], sondeLoc.point[1::-1]])
            print(f"Sonde {sonde} is a {round(dirs.duration/60)} minute drive ({round(dist)} miles) away near {', '.join(sondeLoc.address.split(', ')[-3:])}")
