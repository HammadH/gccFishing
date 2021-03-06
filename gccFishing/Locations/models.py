

from django.db import models
from sorl.thumbnail import ImageField
from django.core.urlresolvers import reverse
from django.contrib import admin

from django.conf import settings
from autoslug import AutoSlugField
from smart_selects.db_fields import ChainedForeignKey


def image_path(instance, filename):
	path = "Images/Locations/{place}/{file}".format(place = instance.name, file=filename)
	return path



class Country(models.Model):
		name = models.CharField("Name of Country", max_length = 100, unique = True)
		slug = AutoSlugField(populate_from = 'name')
		image = ImageField(upload_to = image_path)
		flag = ImageField (upload_to = image_path)

		def __unicode__(self):
			return self.name

		def get_absolute_url(self):
			return reverse('insideCountry', kwargs = {'country_slug': self.slug})	 

		def get_member_count(self):
			members = self.members.count()
			return members

		def get_city_count(self):
			cities = self.cities.count()
			return cities



class City(models.Model):
	name = models.CharField("Name of City", max_length=100)
	image = ImageField(upload_to=image_path)
	slug = AutoSlugField(populate_from='name', unique = True)
	__lng = models.CharField("Longitude", max_length=100, db_column = 'lng', blank= True)
	__ltd = models.CharField("Latitude", max_length=100, db_column='ltd', blank=True)
	country = models.ForeignKey(Country, related_name = 'cities')

	def __unicode__(self):
			return self.name

	@property
	def lng(self):
		return self.__lng 

	@lng.setter
	def lng(self, value):
		if value == '':
			self.__lng = '0.0'
		else:
			self.__lng = value

	@property
	def ltd(self):
		return self.__ltd 

	@ltd.setter
	def ltd(self, value):
		if value == '':
			self.__ltd = '0.0'
		else:
			self.__ltd = value



	def get_absolute_url(self):
		return reverse('insideCity_wall', kwargs= {'country_slug': self.country.slug, 'city_slug' : self.slug}) 


	def get_member_count(self):
		members = self.members.count()
		return members



class Location(models.Model):
	country = models.ForeignKey(Country)
	city = ChainedForeignKey(
		City,
		chained_field="country",
		chained_model_field="country",
		show_all=False,
		auto_choose=True
		)

	def __unicode__(self):
		return self.country.name



admin.site.register(Country)
admin.site.register(City)
admin.site.register(Location)