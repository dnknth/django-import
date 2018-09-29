from django.contrib.admin import SimpleListFilter
from django.contrib.gis import admin
from django.db.models import ForeignKey
from django.forms.widgets import Select
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from .models import *


@admin.register( TimeZone)
class TimeZoneAdmin( admin.OSMGeoAdmin):

    class AreaListFilter( SimpleListFilter):
        'Filter time zones by area'
        title = _('area')

        # Parameter for the filter that will be used in the URL query.
        parameter_name = 'area'

        def lookups( self, request, model_admin):
            return sorted( frozenset( (tz.area(), tz.area())
                for tz in TimeZone.objects.all()))

        def queryset( self, request, queryset):
            if queryset.model is TimeZone and self.value():
                return queryset.filter( tzid__startswith=self.value())
            else:
                return queryset

    list_filter = ( AreaListFilter, )
    list_display = ('__str__', 'name', 'utc_offset')
    search_fields = ( 'tzid', )


@admin.register( CityCenter)
class CityCenterAdmin( admin.OSMGeoAdmin):
    list_display = ('__str__', 'sov0', 'adm1')
    list_filter = ( 'worldcity', 'megacity', 'sov0' )
    search_fields = ( 'name', )


@admin.register( Location)
class LocationAdmin( admin.OSMGeoAdmin):
    list_display = ( 'city', 'post_code', 'country' )
    search_fields = ( 'city', 'post_code' )
    list_filter = ( 'country', )


@admin.register( NetBlock)
class NetBlockAdmin( admin.ModelAdmin):
    list_display = ( '__str__', 'location' )
    search_fields = ( '^start', )
    list_filter = ( 'location__country', )
    raw_id_fields = ( 'location', )


@admin.register( FedWireInfo)
class FedWireInfoAdmin( admin.ModelAdmin):
    list_display = ( 'bank_name', 'routing_code', 'state', 'city')
    list_filter = ( 'funds_transfer_elegible', 'funds_settlement_only', 'bes_transfer_elegible', 'state')
    search_fields = ( 'bank_name', 'bank_code' )
