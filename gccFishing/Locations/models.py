from django.db import models
from sorl.thumbnail import ImageField
from django.core.urlresolvers import reverse
from django.contrib import admin

from django.conf import settings
from autoslug import AutoSlugField








def image_path(instance, filename):
	path = "Images/Locations/%s"  %filename
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
	name = models.CharField("Name of City", max_length=100, unique = True)
	image = ImageField(upload_to=image_path)
	slug = AutoSlugField(populate_from='name')
		
	

	country = models.ForeignKey(Country, related_name = 'cities')



	def __unicode__(self):
			return self.name

	def get_absolute_url(self):
		return reverse('insideCity', kwargs= {'country_slug': self.country.slug, 'city_slug' : self.slug}) 


	def get_member_count(self):
		members = self.members.count()
		return members



admin.site.register(Country)
admin.site.register(City)
