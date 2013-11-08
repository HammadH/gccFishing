from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.contrib.gis.shortcuts import render_to_kml
from django.http import HttpResponse
from django.template import RequestContext
from Locations.models import Country, City
from spots.models import Spot, Loc

def index(request, *args, **kwargs):
	city_slug = kwargs['city_slug']
	city = City.objects.get(slug = city_slug)
	country = Country.objects.get(slug = kwargs['country_slug'])
	spots = Loc.objects.order_by('name')
	context = {}
	context['city'] = city
	context['country'] = country
	context['waypoints'] = spots
	context['content'] = render_to_string("waypoints.html", {'waypoints': spots})
	
	return render_to_response('spots.html', context, RequestContext(request))