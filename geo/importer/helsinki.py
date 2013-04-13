import os
import csv
import requests
from geo.models import *
from django.conf import settings
from django import db
from django.contrib.gis.gdal import DataSource, SpatialReference, CoordTransform
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Point

MUNI_URL = "http://tilastokeskus.fi/meta/luokitukset/kunta/001-2013/tekstitiedosto.txt"

SERVICE_CATEGORY_MAP = {
    25480: ("library", "Library"),
    28148: ("swimming_pool", "Swimming pool"),
    25402: ("toilet", "Toilet"),
    25344: ("recycling", "Recycling point"),
    25664: ("park", "Park"),
}

def convert_from_gk25(north, east):
    pnt = Point(east, north, srid=3879)
    pnt.transform(PROJECTION_SRID)
    return pnt

class Importer(object):
    def import_municipalities(self):
        s = self.http.open_url(MUNI_URL, "muni")
        # strip first 4 lines of header and any blank/empty lines at EOF
        count = 0
        for line in s.rstrip().split('\n')[4:]:
            dec_line = line.decode('iso8859-1').rstrip().split('\t')
            (muni_id, muni_name) = dec_line
            muni_id = int(muni_id)
            muni_name = muni_name.split(' - ')[0]

            try:
                muni = Municipality.objects.get(id=muni_id)
            except:
                muni = Municipality(id=muni_id, name=muni_name)
                muni.save()
                count += 1
        print "%d municipalities added." % count

    def import_addresses(self):
        f = open(os.path.join(self.data_path, 'pks_osoite.csv'))
        reader = csv.reader(f, delimiter=',')
        reader.next()
        muni_list = Municipality.objects.all()
        muni_dict = {}
        for muni in muni_list:
            muni_dict[muni.name] = muni
            muni.num_addr = Address.objects.filter(municipality=muni).count()
        bulk_addr_list = []
        count = 0
        for idx, row in enumerate(reader):
            street = row[0]
            if not row[1]:
                continue
            num = int(row[1])
            num2 = row[2]
            if not num2:
                num2 = None
            letter = row[3]
            coord_n = int(row[8])
            coord_e = int(row[9])
            muni_name = row[10]
            row_type = int(row[-1])
            if row_type != 1:
                continue
            id_s = "%s %d" % (street, num)
            if id_s == 'Eliel Saarisen tie 4':
                muni_name = 'Helsinki'
            muni = muni_dict[muni_name]
            args = dict(municipality=muni, street=street, number=num, number_end=num2, letter=letter)
            # Optimization: if the muni doesn't have any addresses yet,
            # use bulk creation.
            addr = None
            if muni.num_addr != 0:
                try:
                    addr = Address.objects.get(**args)
                except Address.DoesNotExist:
                    pass
            if not addr:
                addr = Address(**args)

            pnt = convert_from_gk25(coord_n, coord_e)
            #print "%s: %s %d%s N%d E%d (%f,%f)" % (muni_name, street, num, letter, coord_n, coord_e, pnt.y, pnt.x)
            addr.location = pnt
            if not addr.pk:
                bulk_addr_list.append(addr)
            else:
                addr.save()
                count += 1

            if len(bulk_addr_list) >= 1000 or (count > 0 and count % 1000 == 0):
                if bulk_addr_list:
                    Address.objects.bulk_create(bulk_addr_list)
                    count += len(bulk_addr_list)
                    bulk_addr_list = []
                print "%d addresses processed (%d skipped)" % (count, idx + 1 - count)
                # Reset DB query store to free up memory
                db.reset_queries()

        if bulk_addr_list:
            Address.objects.bulk_create(bulk_addr_list)
            bulk_addr_list = []

    def import_pois(self):
        URL_BASE = 'http://www.hel.fi/palvelukarttaws/rest/v2/unit/?service=%d'
        
        muni_dict = {}
        for muni in Municipality.objects.all():
            muni_dict[muni.name] = muni
        
        for srv_id in SERVICE_CATEGORY_MAP.keys():
            cat_type, cat_desc = SERVICE_CATEGORY_MAP[srv_id]
            cat, c = POICategory.objects.get_or_create(type=cat_type, defaults={'description': cat_desc})

            print "\tImporting %s" % cat_type
            ret = requests.get(URL_BASE % srv_id)
            for srv_info in ret.json():
                srv_id = unicode(srv_info['id'])
                try:
                    poi = POI.objects.get(origin_id=srv_id)
                except POI.DoesNotExist:
                    poi = POI(origin_id=srv_id)
                poi.name = srv_info['name_fi']
                poi.category = cat
                if not 'address_city_fi' in srv_info:
                    print "No city!"
                    print srv_info
                    continue
                city_name = srv_info['address_city_fi']
                if not city_name in muni_dict:
                    city_name = city_name.encode('utf8')
                    post_code = srv_info.get('address_zip', '')
                    if post_code.startswith('00'):
                        print "%s: %s (%s)" % (srv_info['id'], poi.name.encode('utf8'), city_name)
                        city_name = "Helsinki"
                    elif post_code.startswith('01'):
                        print "%s: %s (%s)" % (srv_info['id'], poi.name.encode('utf8'), city_name)
                        city_name = "Vantaa"
                    elif post_code in ('02700', '02701', '02760'):
                        print "%s: %s (%s)" % (srv_info['id'], poi.name.encode('utf8'), city_name)
                        city_name = "Kauniainen"
                    elif post_code.startswith('02'):
                        print "%s: %s (%s)" % (srv_info['id'], poi.name.encode('utf8'), city_name)
                        city_name = "Espoo"
                    else:
                        print srv_info
                poi.municipality = muni_dict[city_name]
                poi.street_address = srv_info.get('street_address_fi', None)
                poi.zip_code = srv_info.get('address_zip', None)
                if not 'northing_etrs_gk25' in srv_info:
                    print "No location!"
                    print srv_info
                    continue
                poi.location = convert_from_gk25(srv_info['northing_etrs_gk25'], srv_info['easting_etrs_gk25'])
                poi.save()
