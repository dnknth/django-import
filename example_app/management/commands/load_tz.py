from example_app.models import TimeZone
from importer import *


class Command( ZIPDownloader, ShapeFileImporter):

    help     = "Load time zones into the database."
    url      = 'http://efele.net/maps/tz/world/tz_world_mp.zip'
    pattern  = '*/*.shp'

    model    = TimeZone
    mapping  = { 'tzid' : 'TZID', 'geometry' : 'POLYGON' }
