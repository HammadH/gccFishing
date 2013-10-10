from django.conf.urls import patterns, include, url
from django.conf import settings

from views import countryView, cityView, citywall, conversation_view

urlpatterns = patterns('',

	url(r'^(?P<country_slug>[\w-]+)/$', countryView.as_view(), name= 'insideCountry'),
	url(r'^(?P<country_slug>[\w-]+)/(?P<city_slug>[\w-]+)/$', cityView.as_view(), name = 'insideCity'),
	url(r'^(?P<country_slug>[\w-]+)/(?P<city_slug>[\w-]+)/wall/$', citywall.as_view(), name = 'insideCity_wall'),
	url(r'^(?P<country_slug>[\w-]+)/(?P<city_slug>[\w-]+)/wall/post/(?P<post_id>\d+)/', conversation_view, name = 'conversation'),

	)