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
from django.utils import simplejson

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string, get_template
from django.template import Context



from Locations.models import Country, City, Location
from wall.models import Wallpost, Comment
from notifications.models import Notification 
from onlineuser.models import Online

from django.contrib.auth import authenticate, login, logout
User = get_user_model()
import json

resolve_url_lazy = lazy(resolve_url, str)

from django.forms import EmailField
from django.core.exceptions import ValidationError

CONTENT_TYPE = ['image']






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

	

@sensitive_post_parameters()
@csrf_protect
@never_cache
def loginView(request):
	if request.method == 'POST':
		email = request.POST.get('email', "")
		password = request.POST.get('password', "")
	#	redirect_to = request.REQUEST.get('next', '')	
		try:		
						
			user = authenticate(email = email, password = password)
			
		except:
			return HttpResponse('no such user, please register')		
		if user is not None:
			if user.is_active:
				login(request, user)
				
			else: return HttpResponse('sorry, disabled account, please activate')
		else: return HttpResponse('Incorrect Email and Password ')
		
		return HttpResponseRedirect(reverse('insideCity_wall', kwargs={'country_slug':user.country.slug, 'city_slug':user.city.slug}))

		



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
					image = request.FILES.get('image',settings.DEFAULT_IMAGE_PATH)
					if image == settings.DEFAULT_IMAGE_PATH:
						clean_data['image'] = image
					else:
						clean_data['image'] = self.check_image(image)
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
	
	def check_image(self, image):
			ct = image.content_type.split('/')[0]
			if ct not in CONTENT_TYPE:
				 return settings.DEFAULT_IMAGE_PATH
			else:
				return image
			



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
	member = User.objects.get(id=id)
	member_catches = member.posts.exclude(image='')[:40]
	ctx = {}
	ctx['member']=member
	try:
		
		ctx['last_seen']=Online.objects.last_seen(member) 
	except Online.DoesNotExist:
		ctx['last_seen']=u''

	ctx['row_1'] = member_catches[0:10]
	ctx['row_2'] = member_catches[11:20]
	ctx['row_3'] = member_catches[21:30]
	ctx['row_4'] = member_catches[31:40]

	return render_to_response('profile.html',ctx, RequestContext(request))

class EditProfile(View):
	def get(self, request, *args, **kwargs):
		member = User.objects.get(id=kwargs['id'])
		
		countries = Country.objects.all()
		cities = City.objects.all()
		context={}
		context['member'] = member
		context['countries']=countries
		context['cities']=cities
		return render_to_response('edit_profile.html', context, RequestContext(request))

	def post(self, request, *args, **kwargs):
		user = User.objects.get(id=request.user.id)
		previous_image = user.image
		print previous_image.url
		user.name = request.POST['name']
		user.image = request.FILES.get('image', previous_image)
		user.email = request.POST['email']
		user.country = Country.objects.get(name=request.POST['country'])
		user.city = City.objects.get(name=request.POST['city'])
		user.save()
		return HttpResponseRedirect(reverse('profile', args=(user.id,)))
		 	


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







def country_select(request):
	country = request.POST['country']
	cities = Country.objects.get(name=country).cities.all()
	l = []
	for city in cities:
		l.append(city.name)


	return HttpResponse(json.dumps(l))




def subscription(request, id):
	user = User.objects.get(id=id)
	
	if request.method == 'POST' and request.is_ajax():
		ctx = {}

		if user.email_notification == 1:
			user.email_notification = 0
			user.save()
			if user.email_notification == 0:
				ctx['message'] = u'Ok no more emails..'
				ctx['status'] = u'OFF'
				return HttpResponse(simplejson.dumps(ctx), content_type="application/json")
			else:
				return HttpResponse("Some error occured, please try again.")

		elif user.email_notification == 0:	
			user.email_notification = 1
			user.save()
			if user.email_notification == 1:
				ctx['message'] = u'Emails are on..'
				ctx['status'] = u'ON'
				return HttpResponse(simplejson.dumps(ctx), content_type="application/json")

				
			else:
				ctx['message'] = u'Some error occured :( please try again.'
				return HttpResponse(simplejson.dumps(ctx), content_type="application/json")
			
	
	
	elif request.method == 'GET':

		if user.email_notification == 1:
			user.email_notification = 0
			user.save()
			if user.email_notification == 0:
				return HttpResponse("Ok no more emails..")
			else:
				return HttpResponse("Some error occured, please try again.")

		elif user.email_notification == 0:	
			user.email_notification = 1
			user.save()
			if user.email_notification == 1:
				return HttpResponse("Emails are on..")
			else:
				return HttpResponse("Some error occured, please try again.")


def invite(request):
	

	server_response = {
	'success': '',
	'error':'',
	'message':'',

	}

	temp_ctx = Context()

	if request.is_ajax():
		try:
			EmailField().clean(request.POST['email'])
		except ValidationError:
			server_response['success'] = 0
			server_response['error'] = 1
			server_response['message'] = u"Please enter a valid email address"
			return HttpResponse(simplejson.dumps(server_response), content_type="application/json")
		email = request.POST['email']
		
		if request.user.is_authenticated():
			temp_ctx['name'] = request.user.name
		else:
			temp_ctx['name']= u"a member"

		message_temp = get_template('invitation.html')
		message = message_temp.render(temp_ctx)

		email = EmailMultiAlternatives("Invitation to join the Club!", message, 'Gulf Fishing Club <register@gccfishing.com>', [email] )
		email.attach_alternative(message, 'text/html')
		if email.send():
			server_response['success']=1
			server_response['error']=0
			server_response['message']='Thank you! Invitation sent..'

			return HttpResponse(simplejson.dumps(server_response), content_type="application/json")
		else:
			server_response['success']=0
			server_response['error']=1
			server_response['message']='Some error occured! Try again'			
			return HttpResponse(simplejson.dumps(server_response), content_type="application/json")


	else:
		return
		#must implement








		