from django.contrib.gis.db import models

class Municipality(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

# For municipality names in other languages
class MunicipalityName(models.Model):
    municipality = models.ForeignKey(Municipality)
    language = models.CharField(max_length=8)
    name = models.CharField(max_length=50)

class MunicipalityBoundary(models.Model):
    municipality = models.OneToOneField(Municipality)
    borders = models.MultiPolygonField()

    objects = models.GeoManager()

class Address(models.Model):
    street = models.CharField(max_length=50, db_index=True)
    number = models.PositiveIntegerField()
    letter = models.CharField(max_length=2, blank=True, null=True)
    location = models.PointField()
    municipality = models.ForeignKey(Municipality, db_index=True)

    objects = models.GeoManager()

    class Meta:
        unique_together = (('municipality', 'street', 'number', 'letter'),)
