import logging



from django.views.generic.base import View 
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from models import Country, City
from django.template import RequestContext, Context 

from django.core.urlresolvers import reverse
from wall.models import Wallpost, Comment
from voting.models import Vote

from django.utils import simplejson
from django.forms.models import model_to_dict
from django.core import serializers


from django.contrib.auth import get_user_model

User = get_user_model()







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
		return render_to_response(template_name, context, RequestContext(request))


	
	def post(self, request, *args, **kwargs):       #not the best implementation!
		
		redirect_to = request.path
	
		post = request.POST.copy()
		if post.has_key('email') and post.has_key('password'):
			return HttpResponseRedirect(reverse('login', request))

		

		elif post.has_key('wallpost'):
			if request.user.is_authenticated():
				if post['wallpost'] =='':
						return HttpResponseRedirect(redirect_to)
				else:
					post = self.create_wallpost(request)
					if post:
						return HttpResponseRedirect(redirect_to)
					else:
						return HttpResponse('post not created')		
			else:
				return HttpResponse('Please login to post')

			

	def get_context_data(self, city_slug):
		context = {}
		try:
			city = City.objects.get(slug=city_slug)
		except City.DoesNotExist:
			return None
		context['city'] = city
		context['posts'] = city.posts.order_by('-posted_on')[:25] 
		context['members_count'] = city.members.count()
		context['members'] = city.members.order_by('reputation')
		#context['spots']
		return context




	def create_wallpost(self, request):
		text = request.POST.get('wallpost')
		image = request.FILES.get('wallimage', '')
		user = request.user
		city_slug = request.POST.get('city_slug')
		city = City.objects.get(slug=city_slug)
		country_slug = request.POST.get('country_slug')
		country = Country.objects.get(slug=country_slug)
		try:
			post = Wallpost.objects.create_post(user, country, city, image, text)   # post is object
		except:
			return HttpResponse('some error in posting')
		return post



def conversation_view(request, country_slug, city_slug, post_id):
	if request.user.is_authenticated():
		if request.method == "POST":
			
			text = request.POST['comment']
			posted_by = request.user
			post_id = request.POST['post_id']
			post = Wallpost.objects.get(id=post_id)
			next= request.GET.get('next')
			try:
				comment = Comment.objects.create_comment(text, posted_by, post)
				return HttpResponseRedirect(next)
			except:
				return HttpResponse('some error in posting')
		
		else:
			post = Wallpost.objects.get(id=post_id)
			return render_to_response('conversation.html', {'post':post, 'user': request.user}, RequestContext(request))

	else:
		return render_to_response('page_not_found.html')	


def ajax_Upvote(request):
	if request.user.is_authenticated():
		post_id = request.POST.get('post_id')
		post = Wallpost.objects.get(id=post_id)
		voter = request.user
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
		image = request.FILES.get('city_image', 'Images/Locations/default_city.jpg')		 
		city = City.objects.create(name=name, country=country, image=image)
		if city is not None:
			return render_to_response("city_created.html")
		else:
			return HttpResponse("some error occured! we apologize.. please report to us and we will fix it")



















