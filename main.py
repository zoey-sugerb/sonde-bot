from geopy.geocoders import ArcGIS
from geopy.distance import distance
from routingpy.routers import OSRM
import configparser

# Set up config parser, locator, and router
config = configparser.ConfigParser()
locator = ArcGIS()
router = OSRM(base_url='https://routing.openstreetmap.de/routed-car')

# Read in configuration
config.read('config.ini')

# Get address
addr = config['Location']['Address']
homeLoc = locator.geocode(addr)

# Get destination location
dest = input("Destination address:")
destLoc = locator.geocode(dest)

# Get directions
dirs = router.directions([homeLoc.point[1::-1], destLoc.point[1::-1]])
print(f"Route is {dirs.distance/1000}km and takes {dirs.duration/60}min")
