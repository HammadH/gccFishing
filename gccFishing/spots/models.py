from django.contrib.gis.db import models
from django.contrib import admin
from geoposition.fields import GeopositionField

class Spot(models.Model):

    name = models.CharField(max_length=32)
    position = GeopositionField()

    objects = models.GeoManager()


    def __unicode__(self):
        return '%s' % (self.name)

class Loc(models.Model):
	name = models.CharField(max_length=50)
	description = models.TextField()
	rating = models.IntegerField()
	geometry = models.PointField(srid=4326)
	objects = models.GeoManager()

	def __unicode__(self):
		return self.name

admin.site.register(Spot)
admin.site.register(Loc)
