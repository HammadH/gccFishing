from django.conf.urls import patterns, include, url
from django.conf import settings


from views import countryView, cityView, citywall, conversation_view, citySpots, cityItems, cityOffshore, cityFishes, cityScuba 

urlpatterns = patterns('',

	url(r'^(?P<country_slug>[\w-]+)/$', countryView.as_view(), name= 'insideCountry'),
	url(r'^(?P<country_slug>[\w-]+)/(?P<city_slug>[\w-]+)/$', cityView.as_view(), name = 'insideCity'),
	url(r'^(?P<country_slug>[\w-]+)/(?P<city_slug>[\w-]+)/wall/$', citywall.as_view(), name = 'insideCity_wall'),
	url(r'^(?P<country_slug>[\w-]+)/(?P<city_slug>[\w-]+)/spots/', include('spots.urls')),
	url(r'^(?P<country_slug>[\w-]+)/(?P<city_slug>[\w-]+)/items/$', cityItems.as_view(), name = 'insideCity_items'),
	url(r'^(?P<country_slug>[\w-]+)/(?P<city_slug>[\w-]+)/offshore/$', cityOffshore.as_view(), name = 'insideCity_offshore'),
	url(r'^(?P<country_slug>[\w-]+)/(?P<city_slug>[\w-]+)/fishes/$', cityFishes.as_view(), name = 'insideCity_fishes'),
	url(r'^(?P<country_slug>[\w-]+)/(?P<city_slug>[\w-]+)/scuba/$', cityScuba.as_view(), name = 'insideCity_scuba'),
	url(r'^(?P<country_slug>[\w-]+)/(?P<city_slug>[\w-]+)/wall/post/(?P<post_id>\d+)/', conversation_view, name = 'conversation'),

	)