import datetime

from django.db import models
from django.contrib.auth import get_user_model
from sorl.thumbnail import ImageField
from django.core.validators import MaxValueValidator
from django.contrib import admin
from django.conf import settings
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from Locations.models import City, Country 

from notifications import notify


User = get_user_model()



def Imagepost_path(instance, filename):
	path = "Images/%s"	%filename
	return path 
	



class WallpostManager(models.Manager):
	def create_post(self, author, country, city, image = None, text = None):
		try:
			
			post = self.create(author=author, country= country, city=city, image=image, text=text)
		
		except:
			return None
		return post


	def delete_post(self):
		try:
			self.delete()
		except:
			return False
		return True





class Wallpost(models.Model):
	
	author = models.ForeignKey(User, related_name='posts')
	posted_on = models.DateTimeField(auto_now_add = True)
	points = models.IntegerField(default = 0 )	# relate this to user reputation	
	city = models.ForeignKey(City, related_name='posts', null=True)
	country = models.ForeignKey(Country, related_name='posts', null=True)

	image = ImageField(upload_to = Imagepost_path, null = False, blank = True)
	text = models.TextField(null = True, blank = True) #should be made to show only little text
	
	objects = WallpostManager()

	def __unicode__(self):
		return u"post of %s" %self.author.name
	
	
	def get_absolute_url(self):
		return reverse('views.conversation_view', kwargs={'post_id' :self.id})

	def increase_points(self):
		self.points = self.points + 1
		

	def get_post_comments(self):
		try:
			comments = self.comments.order_by('posted_on')
		except:
			return None
		return comments

	def get_comments_count(self):
		try: 
			comments = self.get_post_comments()
		except:
			count = 0
			return count
		count = comments.count()
		return count

	def save_points(self):
		from voting.models import Vote
		score_dict = Vote.objects.get_score(self)
		self.points = score_dict['score']
		self.save()
		return True

	def get_points(self):
		return self.points




class CommentManager(models.Manager):

	def create_comment(self, text, posted_by, post):
		try:
			new_comment = self.create(text = text, author = posted_by, post = post)
		except:
			return None
		
		post_save.send(sender=self.__class__, instance = new_comment)
		
		return new_comment


class Comment(models.Model):
		author = models.ForeignKey(User, related_name = 'comments', null= True)
		posted_on = models.DateTimeField(auto_now_add = True)
		text = models.TextField()
		post = models.ForeignKey(Wallpost, related_name='comments')

		points = models.IntegerField(default = 0)

		objects = CommentManager()






class pic(models.Model):
	i = ImageField(upload_to=Imagepost_path)

	







def comment_notification_handler(sender, instance, created, **kwargs):

	
	post = getattr(instance, 'post')
	recipient = post.author
	actor = getattr(instance, 'author')
	verb = 'posted a comment'
	action_object = instance
	target = post
	timestamp = instance.posted_on
	
	if recipient != actor:
		notify.send(sender= instance, recipient = recipient, actor = actor, verb = verb, target=target, timestamp=timestamp)
	else:
		pass


post_save.connect(comment_notification_handler, sender = Comment, dispatch_uid='comment_posted_notification')





admin.site.register(Wallpost)


admin.site.register(Comment)