from django.conf.urls import patterns, include, url
from django.conf import settings


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from authtools.urls import *
from views import mainView, registration, loginView, logoutView, activate, profile,   \
notifications_view, process_notification_and_redirect_view, indexView, test_jfu, loc, country_select
from django.views.generic import TemplateView
from Locations import urls
from django.contrib.auth import get_user_model
from django.views.generic.edit import CreateView
from Locations.models import City

import spots

from Locations.views import countryView, process_up_vote, process_down_vote,ajax_Upvote, ajax_Downvote, addCity

import notifications
import uploadify

User = get_user_model()

urlpatterns = patterns('',
    # Examples:
    
    url(r'^$', indexView.as_view(), name='index'),

    url(r'^(?P<user_id>\d+)/home/$', mainView.as_view(), name='home'),
    
    
    url(r'^register', registration.as_view(), name='registration'),
    url(r'^thanks', TemplateView.as_view(template_name='thanks.html')),

   
    # url(r'^gccFishing/', include('gccFishing.foo.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('authtools.urls')),

    url(r'^login/', loginView, name = 'login'),
    url(r'^logout/', logoutView, name = 'logout'),
    url(r'^about/', TemplateView.as_view(template_name='about.html'), name = 'about'),
    url(r'^contact/', TemplateView.as_view(template_name='contact.html'), name = 'contact'),

 

    url(r'^activate/(?P<activation_key>\w+)/$', activate, name='activation'),			

    url(r'^profile/(?P<id>\d+)/$', profile, name = 'profile'),	
       
	url(r'^processing_notification/(?P<notification_id>\d+)/', process_notification_and_redirect_view, name = 'process_notification'),
   
    url(r'^jfu/', test_jfu, name='jfu_upload'),
 
    
    url(r'^locations/', include('Locations.urls'), name= 'locations'),
    url(r'^locations/(?P<country_slug>[\w-]+)/(?P<city_slug>[\w-]+)/spots/', include(spots.urls)),

    url(r'voteup/(?P<post_id>\d+)/', process_up_vote, name='upvote'),
    url(r'voteU/', ajax_Upvote, name='upvote_ajax'),
    url(r'voteD/', ajax_Downvote, name='downvote_ajax'),
    url(r'votedown/(?P<post_id>\d+)/', process_down_vote, name='downvote'),

    
    url('^inbox/notifications/', include(notifications.urls)),

    url(r'^(?P<user_id>\d+)/notifications/', notifications_view, name='notifications'),
    url(r'^chaining/', include('smart_selects.urls')),
    url(r'^user/', CreateView.as_view(model=User)),
    url(r'^loc/', loc.as_view()),

    url(r'^country_select', country_select, name='country_select'),

    url(r'^add_city/', addCity.as_view()),

) 


if settings.DEBUG :
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
