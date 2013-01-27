from django.contrib.gis.geos import Point
from tastypie.resources import ModelResource
from tastypie.exceptions import InvalidFilterError
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.contrib.gis.resources import ModelResource as GeometryModelResource
from tastypie import fields
from geo.models import *
import json

class MunicipalityResource(ModelResource):
    def _convert_to_geojson(self, bundle):
        muni = bundle.obj
        data = {'type': 'Feature'}
        data['properties'] = bundle.data
        data['id'] = bundle.obj.pk
        borders = muni.municipalityboundary.borders
        data['geometry'] = json.loads(borders.geojson)
        bundle.data = data
        return bundle
    def alter_detail_data_to_serialize(self, request, bundle):
        if request.GET.get('format') == 'geojson':
            return self._convert_to_geojson(bundle)
        return bundle
    def alter_list_data_to_serialize(self, request, bundles):
        if request.GET.get('format') != 'geojson':
            return bundles
        data = {'type': 'FeatureCollection'}
        data['meta'] = bundles['meta']
        data['features'] = [self._convert_to_geojson(bundle) for bundle in bundles['objects']]
        return data
    def apply_filters(self, request, filters):
        obj_list = super(MunicipalityResource, self).apply_filters(request, filters)
        if request.GET.get('format') == 'geojson':
            obj_list = obj_list.select_related('municipalityboundary')
        return obj_list
    def dehydrate(self, bundle):
        alt_names = bundle.obj.municipalityname_set.all()
        for an in alt_names:
            bundle.data['name_%s' % an.language] = an.name
        return bundle
    def determine_format(self, request):
        if request.GET.get('format') == 'geojson':
            return 'application/json'
        return super(MunicipalityResource, self).determine_format(request)
    class Meta:
        queryset = Municipality.objects.all().order_by('name').select_related('municipalityboundary')
        resource_name = 'municipality'

class MunicipalityBoundaryResource(GeometryModelResource):
    municipality = fields.ToOneField('geo.api.MunicipalityResource', 'municipality')
    class Meta:
        queryset = MunicipalityBoundary.objects.all()
        resource_name = 'municipality_boundary'
        filtering = {
            'municipality': ALL
        }

class AddressResource(GeometryModelResource):
    municipality = fields.ToOneField('geo.api.MunicipalityResource', 'municipality')

    def apply_sorting(self, objects, options=None):
        if options and 'lon' in options and 'lat' in options:
            try:
                lat = float(options['lat'])
                lon = float(options['lon'])
            except TypeError:
                raise InvalidFilterError("'lon' and 'lat' need to be floats")
            objects = objects.distance(Point(lon, lat, srid=4326)).order_by('distance')
        return super(AddressResource, self).apply_sorting(objects, options)
    
    def dehydrate(self, bundle):
        distance = getattr(bundle.obj, 'distance', None)
        if distance is not None:
            bundle.data['distance'] = distance
        print bundle
        return bundle

    class Meta:
        queryset = Address.objects.all()
        filtering = {
            'municipality': ALL,
            'street': ALL,
            'number': ALL,
            'letter': ALL,
            'location': ALL,
        }
