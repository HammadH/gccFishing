from django.conf.urls.defaults import *


from views import index

urlpatterns = patterns('',

	url(r'^$', index, name='spots-index'),


	)