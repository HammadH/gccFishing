from django.conf.urls import *


form views import Wallview





urlpatterns = patterns ('',

	url(r'^$', Wallview.as_view(), name = 'wall'),

)
