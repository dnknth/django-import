# What's this?

Utility classes to static data sets into [Django](https://www.djangoproject.com) models with a minimum of fuss. Includes an example application with importers for:

- Arbitrary text formats, e.g. [FRB routing codes](example_app/management/commands/load_fedwire.py),
- CSV, e.g. [Maxmind Geo IPs](example_app/management/commands/load_geoip.py). TODO: the Geo IP format used by the examples has been [discontinued](https://support.maxmind.com/geolite-legacy-discontinuation-notice/), code is not yet updated.
- ESRI shape files for [GeoDjango](https://docs.djangoproject.com/en/2.1/ref/contrib/gis/), e.g. [Naturalearth world cities](example_app/management/commands/load_cities.py).

Datasets can be loaded from disk or via HTTP and extracted from ZIP archives or plain files.

The example app uses SpatiaLite, see [installation instructions](https://docs.djangoproject.com/en/2.1/ref/contrib/gis/install/spatialite/). The [settings](example_app/settings.py) are for Mac OS with [Homebrew](https://brew.sh).

# How it works

Importers are Django [management commands](https://docs.djangoproject.com/en/2.1/howto/custom-management-commands/) derived from `ParsingImporter` or `ShapeFileImporter`. Mixin classes are used to transfer, extract and load datasets in various formats:

- `Loader` mixins retrieve the data set from disk or via HTTP.
- `Reader` mixins extract the individual records from the set.
- `Importer` classes provide the basic control flow to load data sets. 

The behaviour is controlled by importer attributes that are evaluated by the mixin classes. Reasonable defaults are provided where possible. See the [examples](example_app/management/commands/) for real-world usage.

# Q&A

- Q: Why are imports tied to Django [management commands](https://docs.djangoproject.com/en/2.1/howto/custom-management-commands/)? Never heard of *separation of concerns*?
  A: This is for static datasets. Usually, they are loaded just once. But also for frequently changing datasets, management commands are ideal for `cron` job updates.
- Q: `importer.py` has a measly 250 lines. Is this a joke?
  A: It's simple, useful and tested in real-life projects. But of course, there are more sophisticed import frameworks [out there](https://django-import-export.readthedocs.io/en/latest/) with more abstraction layers.
- Q: No XML support? What about Excel?
  A: Not supported right now, but should be easy to add. Implementation of an `XMLReader` or `XLSReader` is left open as an exercise.
