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
checkTimeout = int(config['Search']['checkTimeout'])
removeTimeout = int(config['Search']['removeTimeout'])
maxDist = int(config['Search']['maxDist'])

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
        if time() - trackedSondes[sonde]['lastSeen'] >= removeTimeout:
            trackedSondes.pop(sonde)
            print(f"Removing {trackedSondes[sonde]['subtype']} {sonde}, as it has not been seen in over {round(removeTimeout/60)} minutes")
        elif time() - trackedSondes[sonde]['lastChecked'] >= checkTimeout:
            trackedSondes[sonde]['lastChecked'] = time()
            sondeLoc = locator.reverse([trackedSondes[sonde]['lat'], trackedSondes[sonde]['lon']])
            dist = distance(homeLoc.point, [trackedSondes[sonde]['lat'], trackedSondes[sonde]['lon']]).miles
            if dist < maxDist:
                dirs = router.directions([homeLoc.point[1::-1], sondeLoc.point[1::-1]])
                print(f"{trackedSondes[sonde]['subtype']} {sonde} is a {round(dirs.duration/60)} minute drive ({round(dist)} miles) away near {', '.join(sondeLoc.address.split(', ')[-3:])}")
            else:
                print(f"{trackedSondes[sonde]['subtype']} {sonde} is {round(dist)} miles away near {', '.join(sondeLoc.address.split(', ')[-3:])}, which is more than the maximum radius of {maxDist} miles")
