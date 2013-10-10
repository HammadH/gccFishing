from models import Wallpost
from forms import Wallpostform
from django.views.generic.base import View
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth import get_user_model

User = get_user_model()

#class LoginMixin():


class Wallview(View):
	
	
	def get(self, request, *args, **kwargs):	
		context = self.get_context_data()
		return render_to_response('wall.html', context, RequestContext(request))


	def post_wallObject(self, request, *args, **kwargs):
		
		image = request.FILES.get('image', None)
		text = request.POST.get('text', None)
		user = request.user
		try:
			wallpost = Wallpost.objects.create(text = text, image = image, author = user)
			return HttpResponseRedirect('')
		except:
			return 	HttpResponse('You should login to post')



#	def post_commentObject(): #or maybe seperate cbv
				
	def get_context_data(self, **kwargs):
		context = {}
		try:
			posts = Wallpost.objects.order_by('-posted_on')[:20]	
		except Wallpost.DoesNotExist:
			posts = None
		context['posts'] = posts
		return context




