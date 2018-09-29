from example_app.models import NetBlock
from importer import *


class Command( ZIPDownloader, CSVReader, ParsingImporter):

    help = "load geo IP data."
    url  = 'http://geolite.maxmind.com/download/geoip/database/GeoLiteCity_CSV/GeoLiteCity-latest.zip'
    extract   = '*.csv'
    pattern   = '*/GeoLiteCity-Blocks.csv'
    open_mode = 'r'

    model = NetBlock

    batch_size   = 500
    log_interval = 10000
    
    def ip( self, value):
        return '.'.join( map( str, (
            (value >> 24 ) % 256,
            (value >> 16 ) % 256,
            (value >>  8 ) % 256,
            (value       ) % 256)))

    def parse( self, args):
        start, end, loc_id = map( int, args)
        return self.model(
            start=self.ip( start),
            end=self.ip( end),
            location_id=loc_id)

    def get_data( self):
        f = ZIPDownloader.get_data( self)
        f.__next__() # Skip copyright
        f.__next__() # Skip column names
        return f
