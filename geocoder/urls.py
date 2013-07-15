from django.conf.urls import patterns, include, url
from django.conf import settings
from tastypie.api import Api
from munigeo.api import all_resources
from munigeo.views import *
from demo.views import DemoView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

v1_api = Api(api_name='v1')
# geo
for res in all_resources:
    v1_api.register(res())

base_urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'geocoder.views.home', name='home'),
    # url(r'^geocoder/', include('geocoder.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r"^", include(v1_api.urls)),
    url(r"^doc/", include('tastypie_swagger.urls', namespace='tastypie_swagger')),
    url(r"^demo/$", DemoView.as_view()),
    url(r"^google/autocomplete/$", google_autocomplete),
    url(r"^google/details/$", google_details),
)

prefix = getattr(settings, 'URL_PREFIX', '')
urlpatterns = patterns('',
    url("^" + prefix, include(base_urlpatterns))
)
