from example_app.models import CityCenter
from importer import *


class Command( ZIPDownloader, ShapeFileImporter):

    help     = "Load city centers into the database."
    url      = 'https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_populated_places.zip'
    pattern  = '*.shp'

    model    = CityCenter
    mapping  = {
        'name'      : 'NAME',
        'sov0'      : 'SOV0NAME',
        'adm0'      : 'ADM0NAME',
        'adm1'      : 'ADM1NAME',
        'timezone'  : 'TIMEZONE',
        'geometry'  : 'POINT',
        'worldcity' : 'WORLDCITY',
        'megacity'  : 'MEGACITY',
        'meganame'  : 'MEGANAME',
    }
