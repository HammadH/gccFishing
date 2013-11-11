import os

from django.conf import settings

from django.contrib.auth import get_user_model, REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (AuthenticationForm, SetPasswordForm,
                                       PasswordChangeForm, PasswordResetForm)
from django.contrib.auth.tokens import default_token_generator
from django.contrib import auth
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import redirect, resolve_url, render_to_response
from django.utils.functional import lazy
from django.utils.http import base36_to_int, is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import CreateView, TemplateView

from authtools.forms import UserCreationForm
import re
from django.views.generic.base import View
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.template import RequestContext

from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect


from Locations.models import Country, City, Location
from wall.models import Wallpost, Comment, pic
from notifications.models import Notification 

from django.contrib.auth import authenticate, login, logout
User = get_user_model()
import json

resolve_url_lazy = lazy(resolve_url, str)

from django.forms import EmailField
from django.core.exceptions import ValidationError

from jfu.http import upload_receive, UploadResponse






SHA1_RE = re.compile('^[a-f0-9]{40}$')


class indexView(View):
	def get(self, request, *args, **kwargs):
		template_name = 'index.html'
		context = self.get_context_data()
		return render_to_response(template_name, context, RequestContext(request))


	def get_context_data(self):
		context = {}
		context['countries'] = Country.objects.all()		
		return context


class mainView(View):
	
	def get(self, request, *args, **kwargs):
		template_name = 'base.html'
		user_id = kwargs['user_id']
		context = self.get_context_data(user_id)
		return render_to_response(template_name, context, RequestContext(request))


	def get_context_data(self, user_id):
		context = {}
		
		context['user'] = User.objects.get(id=user_id)		
		return context
	
	

@sensitive_post_parameters()
@csrf_protect
@never_cache
def loginView(request):
	if request.method == 'POST':
		email = request.POST.get('email', "")
		password = request.POST.get('password', "")
		redirect_to = request.REQUEST.get('next', '')	
		try:		
						
			user = authenticate(email = email, password = password)
			
		except:
			return HttpResponse('no such user, please register')		
		if user is not None:
			if user.is_active:
				login(request, user)
				
			else: return HttpResponse('sorry, disabled account, please activate')
		else: return HttpResponse('invalid login')
		
		return HttpResponseRedirect(redirect_to)

		



def logoutView(request):
	logout(request)
	return HttpResponseRedirect(reverse('index'))
	
	

class registration(View):
	
	
		
	
	
	def get(self, request, *args, **kwargs):
		template_name = 'register.html'
		context = self.get_context_data()
		return render_to_response(template_name, context, RequestContext(request))

	
	def get_context_data(self):
		context={}
		context['countries']=Country.objects.all()
		context['cities'] = City.objects.all()
		context['locations'] = Location.objects.all()
		return context



	def post(self, request, *args, **kwargs):
		
		success_url = '/thanks/'
		fail_url = '/failed/'
		clean_data = self.get_form_contents(request)
		
		
		new_user = self.create_user(clean_data)
		if new_user is not None:
			return HttpResponseRedirect(success_url)
		else: return HttpResponse("Some error occured! We apologize. Please try later.")
	
	
	def get_form_contents(self, request):
		""" extracts form data from post request and
		returns a dict"""
		error_msg = u"Invalid registration! Please fill appropriately"
		post = request.POST.copy()
		if post['name'] and post['email'] and post['password1'] and post['password2'] and post['country'] and post['city'] is not None:			
			if self.isEmailAddressValid(post['email']):
				if post['password1'] == post['password2']:
					
					clean_data = {}
					clean_data['name'] = post['name']
					clean_data['email'] = post['email']
					clean_data['password1'] = post['password1']
					clean_data['image'] = request.FILES.get('image',settings.DEFAULT_IMAGE_PATH)
					clean_data['country'] = Country.objects.get(name=post['country'])
					clean_data['city'] = City.objects.get(name=post['city'])


					return clean_data
				else:
					error_msg = u" Passwords do not match!"
			
			
			else:
				error_msg = u"Invalid email!"
				
		else:
			error_msg = u"Some Fields Missing! Please enter all the fields" 
					
		
		return HttpResponseServerError(error_msg)
	
	

	def isEmailAddressValid(self, email):
		try:
			EmailField().clean(email)
			return True
		except ValidationError:
			return False
	
			



	def create_user(self, clean_data):
		try:
			return User.objects.create_user(email=clean_data['email'], name = clean_data['name'], image = clean_data['image'], password =clean_data['password1'], country=clean_data['country'], city=clean_data['city'])
		except:
			return None
			
	

def activate(request, activation_key):
	if SHA1_RE.search(activation_key):
		try:
			user = User.objects.get(activation_key = activation_key)
		except :
			return HttpResponse('couldnt find activation key in database!!')

		if not user.activation_key_expired():
			user.is_active = True
			user.activation_key = user.ACTIVATED
			user.save()
			return render_to_response('account_activated.html',{'user':user})
	return HttpResponse('Some error occured, please register again.')




def profile(request, id):
	user = User.objects.get(id=id)
	return render_to_response('profile.html',{'user':user})
		 	


def process_notification_and_redirect_view(request, notification_id):
	notification = Notification.objects.get(id=notification_id)
	notification.mark_as_read()
	post_id = notification.target_object_id
	post = Wallpost.objects.get(id=post_id)
	return HttpResponseRedirect(reverse('conversation', kwargs={'post_id':post_id, 'country_slug':post.country.slug, 'city_slug':post.city.slug}))



def notifications_view(request, user_id):
	if request.user.is_authenticated():
		user = User.objects.get(id=user_id)
		notifications = request.user.notifications.all()
		city = City.objects.get(id = user.city.id)
		return render_to_response('notifications.html', {'notifications':notifications, 'user':user, 'city':city})

	else:
		return render_to_response('page_not_found.html')





def test_jfu(request):

	file = upload_receive(request)
	instance = pic.objects.create(i = file)
	basename = os.path.basename( instance.i.name )
	file_dict = {
        'name' : basename,
        'size' : instance.i.size,

        'url': settings.MEDIA_URL + basename,
        'thumbnail_url': settings.MEDIA_URL + basename,

        
        'delete_type': 'POST',
    }

	return UploadResponse( request, file_dict )

class loc(CreateView):
	model=Location

def country_select(request):
	country = request.POST['country']
	cities = Country.objects.get(name=country).cities.all()
	l = []
	for city in cities:
		l.append(city.name)


	return HttpResponse(json.dumps(l))



	
