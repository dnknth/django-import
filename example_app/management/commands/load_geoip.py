from django.contrib.gis.geos import Point
from importer import *
from example_app.models import Location


class Command( ZIPDownloader, CSVReader, ParsingImporter):

    help      = "load geo IP data."
    url       = 'http://geolite.maxmind.com/download/geoip/database/GeoLiteCity_CSV/GeoLiteCity-latest.zip'
    extract   = '*.csv'
    pattern   = '*/GeoLiteCity-Location.csv'
    model     = Location
    open_mode = 'r'
    encoding  = 'latin1'

    batch_size   = 100
    log_interval = 5000

    def parse( self, args):
        id, country, region, city, post_code, latitude, longitude, metro_code, area_code = args
        return self.model(
            id=id, country=country,
            region=region or None,
            city=city or None,
            post_code=post_code or None,
            metro_code=metro_code or None,
            area_code=area_code or None,
            geometry=Point( float( longitude), float( latitude)))

    def get_data( self):
        f = ZIPLoader.get_data( self)
        f.__next__() # Skip copyright
        f.__next__() # Skip column names
        return f
