# Importer framework for a variety of data sources and formats.
#
# Actual importers should use mixins to control how data is obtained
# and processed, typically via a combination of a Loader and Importer.
# Custom parsing can be added with Readers for plain text and CSV files.


from django.core.management.base import BaseCommand
from fnmatch import fnmatch
from logging import getLogger
import os, requests, tempfile


log = getLogger( __name__)


class BaseImporter( BaseCommand):
    ''' Generic command to import static data into self.model.
        Subclasses must provide a load() method that does the actual
        DB load, and use a Loader mixin to provide input data.
    '''

    # See BaseImporter
    requires_model_validation = True
    can_import_settings = True

    wipe  = True    # Empty table before import?
    model = None    # Override in subclass

    # Main entry point
    def handle( self, *args, **options):
        'Run the import'

        try:
            # Store parameters for subclasses
            self.args    = args
            self.options = options

            # Ensure we can get data before wiping
            data = self.get_data()

            if self.wipe:
                log.info( "Wiping %d records...", self.model.objects.count())
                self.model.objects.all().delete()

            self.load( data)
            self.cleanup()

        except:
            import traceback
            traceback.print_exc()

    def cleanup( self):
        'Post-import cleanup, e.g. temporary files'
        pass


class ParsingImporter( BaseImporter):
    ''' Import data from parsed records.
        Subclasses must implement a parse() method producing
        Django model entities from input data and should
        include use a Reader mixin to obtain input via get_reader().
        get_reader() must return an iterable object such as a
        sequence or a file.
    '''

    batch_size   = None     # Commit to DB in batches of this size
    log_interval = 5000     # log progress after this many inserts

    def load( self, data):
        log.info( "Importing...")
        self.count = 0
        reader = self.get_reader( data)

        # bulk_create is much faster than individual inserts!
        self.model.objects.bulk_create(
            (self.parse( item) for item in reader if self.log( item)),
            batch_size=self.batch_size)
        log.info( "Imported %d records", self.count)

    def log( self, obj=None):
        'Log progress on log_interval inserts'
        if obj:
            self.count += 1
        if self.log_interval and self.count % self.log_interval == 0:
            log.info( "Imported %d records", self.count)
        return obj


class FileReader:
    'Read lines from file-like objects'

    def get_reader( self, data):
        # Files support iteration though lines, so just return the file
        return data


class LineReader:
    ''' Mixin to break a string into lines.
        This makes sense only for buffered text.
        For file-like objects, use FileReader.
    '''

    def get_reader( self, data):
        return data.split( '\n')


class CSVReader:
    'Mixin to read data from a CSV file'

    dialect = 'excel'   # Usually right

    def get_reader( self, data):
        import csv
        return csv.reader( data, self.dialect)


class HTTPLoader:
    'Mixin to load text data from an URL'

    url = None      # Override in subclass

    def get_data( self):
        return requests.get( self.url).text


class FileLoader:
    ''' Mixin to load data from a local file.
        get_file() must be provided by another mixin.
    '''

    open_mode = 'rb'    # Usually right
    encoding = 'UTF8'   # Usually right

    def get_data( self):
        if 'b' in self.open_mode:
            return open( self.get_file(), mode=self.open_mode)
            
        return open( self.get_file(), mode=self.open_mode, 
            encoding=self.encoding)

    def has_file( self):
        return hasattr( self, 'workfile') and self.workfile



class TempFileloader( FileLoader):
    ''' Mixin to handle temporary directories.
        The directory is wiped after import.
    '''

    basedir = None  # Defaults to /tmp

    def get_workdir( self):
        if not hasattr( self, 'workdir'):
            self.workdir = tempfile.mkdtemp( dir=self.basedir)
        return self.workdir

    def cleanup( self):
        log.info( "Cleaning up")
        for dirpath, dirnames, filenames in os.walk( self.workdir, False):
            for f in filenames:
                os.remove( os.path.join( dirpath, f))
            for d in dirnames:
                os.rmdir( os.path.join( dirpath, d))
                os.rmdir( dirpath)


class Downloader( TempFileloader):
    'Mixin to fetch data from self.url into a temporary directory.'

    url = None      # Override in subclass

    def get_file( self):
        if not self.has_file():
            log.info( "Downloading %s" % self.url)
            r = requests.get( self.url)
            fd, self.workfile = tempfile.mkstemp( dir=self.get_workdir())
            with os.fdopen( fd, 'w+b') as out:
                for chunk in r.iter_content( self.chunk_size):
                    out.write( chunk)
        return self.workfile


class PatternMatchingLoader( FileLoader):
    ''' Mixin to pick a work file using a shell pattern.
        This happens typically after archive extraction.
        get_workdir() must be provided elsewhere.
    '''

    pattern = None      # Override in subclass

    def get_file( self):
        if not self.has_file():
            for f in self.list_files():
                if not f.startswith('.') and fnmatch( f, self.pattern):
                    self.workfile = os.path.join( self.get_workdir(), f)
        return self.workfile


class ZIPLoader( TempFileloader, PatternMatchingLoader):
    'Mixin to extract ZIP archives into a temporary directory'

    chunk_size = 4096   # Extraction buffer size
    extract    = '*'    # Glob pattern for archive member names
    archive    = None   # Override in subclass, either path or file

    def list_files( self):
        if not hasattr( self, 'extracted'):
            import zipfile
            self.extracted = []
            with zipfile.ZipFile( self.archive, 'r') as zip:
                for member in zip.infolist():
                    if fnmatch( member.filename, self.extract):
                        log.info( "Extracting %s", member.filename)
                        zip.extract( member, self.get_workdir())
                        self.extracted.append( member.filename)
        return self.extracted


class ZIPDownloader( Downloader, ZIPLoader):
    'Mixin to download and extract a ZIP archive'

    def get_file( self):
        if self.has_file(): return self.workfile

        if not self.archive:
            self.archive = Downloader.get_file( self)
            # Clear workfile to force ZIP extraction
            # Otherwise PatternMatchingLoader.get_file() would fail
            self.workfile = None

        return ZIPLoader.get_file( self)


class ShapeFileImporter( BaseImporter):
    ''' Import data from an ESRI shape file.
        Subclasses must provide a mapping of model field names
        to feature labels in the shape file.
    '''

    strict  = True
    verbose = True  # Log every insert?
    mapping = {}    # Override in subclass!

    def load( self, data):
        from django.contrib.gis.utils import LayerMapping
        LayerMapping( self.model,
            self.get_file(), self.mapping, transform=False).save(
                strict=self.strict, verbose=self.verbose)
