from datetime import datetime
from django.db import models
from django.contrib.gis.db import models as geomodels
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField
import pytz


class TimeZone( geomodels.Model):

    'Time zone map from http://efele.net/maps/tz/world/'

    tzid     = models.CharField( _('time zone ID'), max_length=30)
    geometry = geomodels.MultiPolygonField( geography=True,
               help_text=_('boundary'))

    def __str__(self):
        return self.tzid

    def area( self):
        'Get area name'
        return self.tzid.split( '/')[0]

    def tz( self):
        'Get time zone'
        try:
            return pytz.timezone( self.tzid)
        except pytz.UnknownTimeZoneError:
            pass

    def name( self):
        tz = self.tz()
        return tz.tzname( datetime.utcnow()) if tz else ''

    def utc_offset( self):
        tz = self.tz()
        if not tz: return ''
        secs = tz.utcoffset( datetime.utcnow()).total_seconds()
        hrs = secs / 3600
        mins = secs % 3600 / 60
        return '%02d:%02d' % (hrs, mins)

    class Meta:
        verbose_name = _('time zone')
        verbose_name_plural = _('time zones')
        ordering = ('tzid',)


class CityCenter( geomodels.Model):
    'City center points from naturalearthdata.com'
    # See http://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-populated-places/

    name     = models.CharField( _('name'), max_length=255)
    sov0     = models.CharField( _('sov0 name'), max_length=100)
    adm0     = models.CharField( _('adm0 name'), max_length=100)
    adm1     = models.CharField( _('adm1 name'), max_length=100, blank=True, null=True)
    timezone = models.CharField( _('timezone'), max_length=30, blank=True, null=True)
    worldcity = models.PositiveSmallIntegerField( _('world city'))
    megacity  = models.PositiveSmallIntegerField( _('mega city'))
    meganame  = models.CharField( _('mega name'), max_length=50, blank=True, null=True)

    geometry  = geomodels.PointField( geography=True)

    def __str__( self):
        return self.name

    def tz( self):
        'Get time zone'
        if self.timezone:
            return pytz.timezone( self.timezone)

    class Meta:
        verbose_name = _('city center')
        verbose_name_plural = _('city centers')
        ordering = ('name',)


class Location( geomodels.Model):
    'Geo locations for IP lookup'
    # See http://dev.maxmind.com/geoip/legacy/geolite/

    country    = CountryField( blank=True, null=True)
    region     = models.CharField( max_length=2, blank=True, null=True)
    city       = models.CharField( max_length=255, blank=True, null=True)
    post_code  = models.CharField( max_length=8, blank=True, null=True)
    metro_code = models.IntegerField( blank=True, null=True)
    area_code  = models.CharField( max_length=3, blank=True, null=True)

    geometry   = geomodels.PointField( geography=True)

    def __str__( self):
        if not self.city: return self.country.name
        return '%s, %s' % (self.city, self.country.name)

    class Meta:
        verbose_name = _('location')
        verbose_name_plural = _('locations')
        ordering = ('city',)


class NetBlock( models.Model):
    'Geo-referenced IP address block'
    # See http://dev.maxmind.com/geoip/legacy/geolite/

    start    = models.GenericIPAddressField( protocol='IPv4')
    end      = models.GenericIPAddressField( protocol='IPv4')
    location = models.ForeignKey( Location, on_delete=models.CASCADE)

    def __str__( self):
        return '%s - %s' % (self.start, self.end)

    class Meta:
        verbose_name = _('IP range')
        verbose_name_plural = _('IP ranges')
        ordering = ( 'start', )


class FedWireInfo( models.Model):
    'U.S. bank information from the Federal Reserve (FedWire)'
    # See: http://www.frbservices.org/fedwire/index.html
    # See: http://www.fededirectory.frb.org/format.cfm
    # Source: https://www.frbservices.org/EPaymentsDirectory/fpddir.txt

    route_code_format = '%09d'

    bank_code  = models.BigIntegerField( _('routing code'), unique=True)
    telex_name = models.CharField( _('telegraphic name'), max_length=18) # Should be also unique but we don't need it
    bank_name  = models.CharField( _('bank name'), max_length=36)
    state      = models.CharField( _('state'), max_length=2, blank=True, null=True)
    city       = models.CharField( _('city'), max_length=25)

    funds_transfer_elegible = models.BooleanField( _('funds transfer elegible'), default=False)
    funds_settlement_only   = models.BooleanField( _('funds settlement only'), default=False)
    bes_transfer_elegible   = models.BooleanField( _('book entry securities transfer elegible'), default=False)

    modified = models.DateField( _('last revision'), null=True, blank=True)

    def __str__( self):
        return '%s, %s' % (self.bank_name, self.city)

    @property
    def routing_code( self):
        'Routing code for U.S. accounts'
        return self.route_code_format % self.bank_code

    class Meta:
        ordering = ( 'bank_code',)
        verbose_name = _('FedWire info')
        verbose_name_plural= _('FedWire infos')
        get_latest_by = 'modified'
