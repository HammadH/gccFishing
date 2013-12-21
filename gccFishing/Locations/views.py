import logging
import json


from django.views.generic.base import View 
from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from django.shortcuts import render_to_response
from models import Country, City
from django.template import RequestContext, Context 

from django.core.urlresolvers import reverse
from wall.models import Wallpost, Comment
from voting.models import Vote
from django.views.generic.edit import CreateView
from django.utils import simplejson
from django.forms.models import model_to_dict
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.middleware.csrf import get_token
from onlineuser.models import Online
from django.contrib.auth import get_user_model
from django_youtube.views import upload



User = get_user_model()


CONTENT_TYPE = ['image'] #for checking content_type of uploaded images



class countryView(View):
	


	def get(self, request, *args, **kwargs):
		
		template_name = 'country.html'
		country_slug = kwargs['country_slug']
		context = self.get_context_data(country_slug)
		

		return render_to_response(template_name, context, RequestContext(request))


	def get_context_data(self, country_slug):
		context = {}
		country = Country.objects.get(slug = country_slug)
		context['country'] = country
		context['cities'] = country.cities.all()
		context['cities_count'] = country.get_city_count()
		context['members_count'] = country.get_member_count()
		return context




class cityView(View):
	def get(self, request, *args, **kwargs):
		template_name= 'city.html'
		city_slug=kwargs['city_slug']
		context = self.get_context_data(city_slug)
		return render_to_response(template_name, context, RequestContext(request))

	def get_context_data(self, city_slug):
		context = {}
		context['city'] = City.objects.get(slug=city_slug)
		return context





class citywall(View):
	

	def get(self, request, *args, **kwargs):
		template_name = 'citywall.html'
		city_slug = kwargs['city_slug']
		context = self.get_context_data(city_slug)
		youtube_form_context=upload(request)
		if 'form' in youtube_form_context:
			context['form']=youtube_form_context['form']
			context['post_url']=youtube_form_context['post_url']
			context['next_url']=youtube_form_context['next_url']
		return render_to_response(template_name, context, RequestContext(request))


	
	def post(self, request, *args, **kwargs):       #not the best implementation!
		
		redirect_to = request.path
		
		server_response = {
		'success': 0,
		'error': 0,
		'message': '',
		'template': '',
		} 
		
		template_context = {} # used for rendering post and comment templates
		
		if request.is_ajax():
			if request.user.is_authenticated():
				if request.POST.has_key('comment'):
				
					comment = request.POST.get('comment','')
					if comment == '':
						
						server_response['error'] = 1
						server_response['message'] = u'Nothing to post..'
						
						return HttpResponse(simplejson.dumps(server_response), content_type="application/json")
					else:
						
						post = Wallpost.objects.get(id= request.POST['post_id'])
						new_comment = Comment.objects.create_comment(request.POST['comment'], request.user , post)
					
						template_context['comment']= new_comment
						template_context['author']= new_comment.author
						comment_template = render_to_string("comment.html", template_context)
						
						server_response['success']=1
						server_response['template']=comment_template
						return HttpResponse(simplejson.dumps(server_response), content_type="application/json")
				
				elif request.POST.has_key('wallpost'):
					
					template_context = {}
					text = request.POST.get('wallpost', '')
					
					image = self.check_image(request.FILES.get('wallimage', ''))
					image_1 = self.check_image(request.FILES.get('wallimage_1', ''))
					image_2 = self.check_image(request.FILES.get('wallimage_2', ''))
					image_3 = self.check_image(request.FILES.get('wallimage_3', ''))
					#video_id

					if text == '' and image == '' and image_1 == '' and image_2 =='' and image_3 == '':
						server_response['error'] = 1
						server_response['message'] = u"Nothing to post!"
						return HttpResponse(simplejson.dumps(server_response), content_type="application/json")

					user = request.user
					tags= request.POST.get('tags','')
					
					tags_parsed = self.parse_tags(tags)
					city_slug = request.POST.get('city_slug')
					city = City.objects.get(slug=city_slug)
					country_slug = request.POST.get('country_slug')
					country = Country.objects.get(slug=country_slug)
					
					try:
						post = Wallpost.objects.create_post(user, country, city, image, image_1, image_2, image_3, text)   # post is object
						for tag in tags_parsed:
							post.tags.add(tag)
					except:
						server_response['error']=1
						server_response['message']=u"Oh snap! something went wrong. Try again."
						return HttpResponse(simplejson.dumps(server_response), content_type="application/json")
		
					if post is not None:
						template_context['post'] = post
						template_context['csrfmiddlewaretoken'] = get_token(request)
						post_template= render_to_string('post.html', template_context)
						
						server_response['success']=1
						server_response['template']=post_template
						return HttpResponse(simplejson.dumps(server_response), content_type="application/json")
					else:
						server_response['error']=1
						server_response['message']=u'Some error occured. Please try later.'
						return HttpResponse(simplejson.dumps(server_response), content_type="application/json")
						
			else:
				return HttpResponse("Please Login first.")
		else:
			if request.POST.has_key('comment'):
				context = {}
				post = Wallpost.objects.get(id= request.POST['post_id'])
				new_comment = Comment.objects.create_comment(request.POST['comment'], request.user , post)
				context['comment']= new_comment
				context['author']= new_comment.author
				comment_template = render_to_string("comment.html", context)
				return HttpResponseRedirect(redirect_to, RequestContext(request))

			elif request.POST.has_key('wallpost'):
				context = {}
				text = request.POST.get('wallpost', '')
				image = self.check_image(request.FILES.get('wallimage', ''))
				image_1 = self.check_image(request.FILES.get('wallimage_1', ''))
				image_2 = self.check_image(request.FILES.get('wallimage_2', ''))
				image_3 = self.check_image(request.FILES.get('wallimage_3', ''))
				if text == '' and image == '' and image_1 == '' and image_2 =='' and image_3 == '':
					return HttpResponse("nothing to post!")

				user = request.user
				tags= request.POST.get('tags','')
				tags_parsed = self.parse_tags(tags)
				city_slug = request.POST.get('city_slug')
				city = City.objects.get(slug=city_slug)
				country_slug = request.POST.get('country_slug')
				country = Country.objects.get(slug=country_slug)
				try:
					post = Wallpost.objects.create_post(user, country, city, image, image_1, image_2, image_3, text)   # post is object
					for tag in tags_parsed:
						post.tags.add(tag)
				except:
					return HttpResponse('some error in posting')
		
				if post is not None:
					context['post'] = post
					context['csrfmiddlewaretoken'] = get_token(request)
					post_template= render_to_string('post.html', context)
					return HttpResponseRedirect(redirect_to, RequestContext(request))
				else:
					return HttpResponse("Some error occured, please try later.")

			

	def check_image(self, image):
		if image is not '':
			ct = image.content_type.split('/')[0]
			if ct not in CONTENT_TYPE:
				return HttpResponse('The uploaded file is not an image!')
			else:
				return image
		else:
			return ''

				
			

	def get_context_data(self, city_slug):
		context = {}
		try:
			city = City.objects.get(slug=city_slug)
		except City.DoesNotExist:
			return None
		context['city'] = city
		
		if city.ltd and city.lng:
			city_map_ltd = self.convert_string_to_float(city.ltd)
			city_map_lng = self.convert_string_to_float(city.lng)
		
			context['city_map_ltd'] =city_map_ltd  # required for google map
			context['city_map_lng'] =city_map_lng
			print city_map_lng
			print city_map_ltd

		context['posts'] = city.posts.order_by('-posted_on').select_related() 
		context['members_count'] = city.members.count()
		context['members'] = city.members.order_by('-reputation').select_related()
		context['online_members']= Online.objects.online_users(city_slug)
		#context['spots']
		return context


	def convert_string_to_float(self, string):
		import re
		r = re.compile(r'(\d+\.\d+)')
		temp = float(r.match(string).group(1))
		return temp

	def parse_tags(self, tags):
		parsed_tags = tags.split()
		return parsed_tags



def edit_comment(request, comment_id):
	context = {}
	if request.method == 'POST':
		if request.is_ajax():
			comment = Comment.objects.get(id = comment_id)
			comment.text = request.POST['comment']
			comment.save()
			context['comment'] = comment
			context['author'] = comment.author
			comment_template = render_to_string('comment.html', context)
			return HttpResponse(simplejson.dumps(comment_template), content_type="application/json")
		else:
			comment = Comment.objects.get(id = comment_id)
			comment.text = request.POST['comment']
			comment.save()
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
				
	else:
		comment = Comment.objects.get(id = comment_id)
		author = comment.author
		context['comment'] = comment
		context['author'] = author
		comment_form = render_to_string('comment_edit_form.html', context, RequestContext(request))
		return HttpResponse(simplejson.dumps(comment_form), content_type="application/json")


def delete_comment(request, comment_id):
	if request.method == "POST":
		if request.is_ajax():
			comment = Comment.objects.get(id = comment_id)
			response = {}
			try:
				comment.delete()
				response['status'] = 1
				return HttpResponse(simplejson.dumps(response), content_type="application/json")
			except:
				response['status'] = 0
				return HttpResponse(simplejson.dumps(response), content_type="application/json")

		else:
			comment = Comment.objects.get(id = comment_id)
			comment.delete()
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



def conversation_view(request, country_slug, city_slug, post_id):
	if request.method == 'POST':
		if request.is_ajax():
			if request.user.is_authenticated():
				if request.POST.has_key('comment'):
				
					comment = request.POST.get('comment','')
					print comment
					if comment == '':
						context = {}
						context['message'] = u'Nothing to post..'
						
						return HttpResponse(simplejson.dumps(context), content_type="application/json")
					else:
						context = {}
						post = Wallpost.objects.get(id= request.POST['post_id'])
						new_comment = Comment.objects.create_comment(request.POST['comment'], request.user , post)
					
						context['comment']= new_comment
						context['author']= new_comment.author
						comment_template = render_to_string("comment.html", context)
						return HttpResponse(simplejson.dumps(comment_template), content_type="application/json")
	
			else:	
				return render_to_response('page_not_found.html')		
	else:
		try:
			post = Wallpost.objects.get(id=post_id)
			return render_to_response('conversation.html', {'post':post, 'user': request.user}, RequestContext(request))
		except:
			return render_to_response('page_not_found.html')
				





def ajax_Upvote(request):
	if request.user.is_authenticated():
		post_id = request.POST.get('post_id')
		post = Wallpost.objects.get(id=post_id)
		voter = request.user
		if post.author == voter:
			response_dict={
			'error': True,
			'message': u"Come on now, you cant vote your own post." 
			}

			return HttpResponse(simplejson.dumps(response_dict), content_type="application/json")
		vote_obj = Vote.objects.record_vote(post, voter, +1)
		post.save_points()
		points = post.get_points()
		author_rep = post.author.reputation
		response_dict = {
		'success' : True,
		'points' : points,
		'author_rep': author_rep,
		}
		return HttpResponse(simplejson.dumps(response_dict), content_type="application/json")

		

	else:
		return HttpResponse(simplejson.dumps('Please login to vote.'), content_type="application/json")

def ajax_Downvote(request):
	if request.user.is_authenticated():
		post_id = request.POST.get('post_id')
		post = Wallpost.objects.get(id=post_id)
		voter = request.user
		vote_obj = Vote.objects.record_vote(post, voter, -1)
		post.save_points()
		points = post.get_points()
		author_rep = post.author.reputation
		response_dict = {
		'success' : True,
		'points' : points,
		'author_rep': author_rep,
		}
		return HttpResponse(simplejson.dumps(response_dict), content_type="application/json")

		

	else:
		return HttpResponse(simplejson.dumps('Please login to vote.'), content_type="application/json")



		

	








def process_up_vote(request, post_id):
	if request.user.is_authenticated():
		next = request.GET.get('next')
		
		if request.is_ajax():
		
			post_id = request.POST.get('post_id')
			voter = request.user
			post = Wallpost.objects.get(id=post_id)
			
			if post.author == voter:
				return HttpResponse(simplejson.dumps("Come on now, you cant vote your own post."), content_type="application/json")
			vote_obj = Vote.objects.record_vote(post, voter, +1)
			post.save_points()
			points = post.get_points
			author_rep = post.author.reputation
			response_dict = {
			'success' : True,
			'points' : points,
			'author_rep': author_rep,
			}
			return HttpResponse(simplejson.dumps(response_dict), content_type="application/json")
		else:
			if request.method == 'POST':
				post_id = request.POST.get('post_id')
				voter = request.user
				post = Wallpost.objects.get(id=post_id)
				vote_obj = Vote.objects.record_vote(post, voter, +1)
				post.save_points()
				#user = post.author
				#user.update_rep()
			
			return HttpResponseRedirect(next)
	else:
		return HttpResponse('login Please')


	

def process_down_vote(request, post_id):
	if request.user.is_authenticated():
		next = request.GET.get('next')
		if request.is_ajax():
			post_id = request.POST.get('post_id')
			voter = request.user
			post = Wallpost.objects.get(id=post_id)
			vote_obj = Vote.objects.record_vote(post, voter, -1)
			post.save_points()
			return HttpResponseRedirect(next)
		else:
			if request.method == 'POST':
				post_id = request.POST.get('post_id')
				voter = request.user
				post = Wallpost.objects.get(id=post_id)
				vote_obj = Vote.objects.record_vote(post, voter, -1)
				post.save_points()
				#user = post.author
				#user.update_rep()
			
				return HttpResponseRedirect(next)
			else:
				return HttpResponse('no post data!')
	else:
		return HttpResponse('login Please')

class citySpots(View):

	def get(self, request, *args, **kwargs):
		template_name = 'spots.html'
		city_slug = kwargs['city_slug']
		context = self.get_context_data(city_slug)
		return render_to_response(template_name, context, RequestContext(request))

	def get_context_data(self, city_slug):
		context = {}
		try:
			city = City.objects.get(slug=city_slug)
		except City.DoesNotExist:
			return None
		context['city'] = city
		
		#context['spots']
		return context

class cityOffshore(View):

	def get(self, request, *args, **kwargs):
		city_slug = kwargs['city_slug']
		template_name = 'offshore.html'
		context = self.get_context_data(city_slug)
		return render_to_response(template_name, context, RequestContext(request))

	def get_context_data(self, city_slug):
		context = {}
		try:
			city = City.objects.get(slug=city_slug)
		except City.DoesNotExist:
			return None
		context['city'] = city
		
		#context['spots']
		return context


class cityItems(View):

	def get(self, request, *args, **kwargs):
		city_slug = kwargs['city_slug']
		template_name = 'items.html'
		context = self.get_context_data(city_slug)
		return render_to_response(template_name, context, RequestContext(request))

	def get_context_data(self, city_slug):
		context = {}
		try:
			city = City.objects.get(slug=city_slug)
		except City.DoesNotExist:
			return None
		context['city'] = city
		
		#context['spots']
		return context


class cityFishes(View):

	def get(self, request, *args, **kwargs):
		template_name = 'fishes.html'
		city_slug = kwargs['city_slug']
		context = self.get_context_data(city_slug)
		return render_to_response(template_name, context, RequestContext(request))

	def get_context_data(self, city_slug):
		context = {}
		try:
			city = City.objects.get(slug=city_slug)
		except City.DoesNotExist:
			return None
		context['city'] = city
		
		#context['spots']
		return context

class cityScuba(View):

	def get(self, request, *args, **kwargs):
		template_name = 'scuba.html'
		city_slug = kwargs['city_slug']
		context = self.get_context_data(city_slug)
		return render_to_response(template_name, context, RequestContext(request))

	def get_context_data(self, city_slug):
		context = {}
		try:
			city = City.objects.get(slug=city_slug)
		except City.DoesNotExist:
			return None
		context['city'] = city
		
		#context['spots']
		return context



class addCity(View):
	def get(self, request, *args, **kwargs):
		countries = Country.objects.all()
		return render_to_response('addCity.html', {'countries':countries}, RequestContext(request))

	def post(self, request, *args, **kwargs):

		
			
		name = request.POST['name']
		country = Country.objects.get(name=request.POST['country'])
		image_temp = request.FILES.get('city_image', 'Images/Locations/default_city.jpg')
		if image_temp != 'Images/Locations/default_city.jpg':
			image = self.check_image(image_temp)
		else:
			image = image_temp
		lng = request.POST.get('lng')
		ltd = request.POST.get('ltd' )
			 
		city = City.objects.create(name=name, country=country, image=image, lng=lng, ltd=ltd)
		if city is not None:
			return HttpResponseRedirect(reverse('insideCity_wall',  kwargs={'country_slug':country.slug, 'city_slug':city.slug}))
		else:
			return HttpResponse("some error occured! ")

	def check_image(self, image):
			ct = image.content_type.split('/')[0]
			if ct not in CONTENT_TYPE:
				return 'Images/Locations/default_city.jpg'
			else:
				return image
		























