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

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
from django.template import Context


from notifications import notify
from taggit.managers import TaggableManager
from onlineuser.models import Online

User = get_user_model()



def Imagepost_path(instance, filename):
	path = "Images/Wallimages/{user}/{file}".format(user=instance.author.name, file=filename)
	return path 
	



class WallpostManager(models.Manager):
	def create_post(self, author, country, city, image = None, image_1=None, image_2=None, image_3=None, text = None):
		try:
			post = self.create(author=author, country= country, city=city, image=image, image_1=image_1, image_2=image_2, image_3=image_3, text=text)
			post_save.send(sender = self.__class__, instance = post)
			return post
		except:
			return None
		


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

	

	image = ImageField(upload_to = Imagepost_path, null = True, blank = True)
	image_1 = ImageField(upload_to = Imagepost_path, null = True, blank = True)
	image_2 = ImageField(upload_to = Imagepost_path, null = True, blank = True)
	image_3 = ImageField(upload_to = Imagepost_path, null = True, blank = True)

	

	text = models.TextField(null = True, blank = True) #should be made to show only little text
	
	objects = WallpostManager()
	tags = TaggableManager()

	def __unicode__(self):
		return u"post of %s" %self.author.name
	
	
	def get_absolute_url(self):
		return reverse('views.conversation_view', kwargs={'post_id' :self.id})

	def increase_points(self):
		self.points = self.points + 1
		


	def get_post_comments_all(self):
		try:
			comments = self.comments.order_by('posted_on')
		except:
			return None
		return comments

	def get_comments_count(self):
		try: 
			comments = self.get_post_comments_all()
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

	def create_comment(self, text, author, post):
		
		new_comment = self.create(text = text, author = author, post = post)
		post_save.send(sender=self.__class__, instance = new_comment)	
		return new_comment
		
		
		
		
		


class Comment(models.Model):
		author = models.ForeignKey(User, related_name = 'comments')
		posted_on = models.DateTimeField(auto_now_add = True)
		text = models.TextField()
		post = models.ForeignKey(Wallpost, related_name='comments')
		points = models.IntegerField(default = 0)

		objects = CommentManager()




	
def comment_notification_handler(sender, instance, created, **kwargs):  #use celery here

	
	post = getattr(instance, 'post')
	post_author = post.author
	comment_actor = getattr(instance, 'author')
	recipients = set()
	if comment_actor != post_author:
		recipients.add(post_author)
	for comment in post.get_post_comments_all():
		recipients.add(comment.author)
	try:
		recipients.remove(comment_actor)
	except KeyError:
		pass
	

	verb = 'posted a comment-'
	action_object = instance
	target = post
	timestamp = instance.posted_on
	
	for recipient in recipients:
		notify.send(sender= instance, recipient=recipient,  actor = comment_actor, verb = verb, target=target, timestamp=timestamp)

	



def send_emails(sender, instance, created, **kwargs):  #use celery here
	
	if created:
		return
		if isinstance(instance, Wallpost):
			author = getattr(instance, 'author')
			city = getattr(instance, 'city')
			email_list = []
			users = User.objects.filter(city=city, email_notification=1).exclude(id=author.id)
			for user in users:
				if user.is_active == True:
					if user.online.online() == False:
						email_list.append(user.email)
					else:
						pass
				else:
					pass	
			print email_list				

			context = Context()
			context['post'] = instance
			context['author'] = author
			context['city'] = city
			
			subject = getattr(instance, 'text')
			if subject == '':
				subject = render_to_string('post_created.txt', context)
				body_html = get_template('post_created_body_empty.html')
				body_txt = render_to_string('post_created_body_empty.txt')
			else:
				body_html = get_template('post_created_body.html')
				body_txt = render_to_string('post_created_body.txt')

			body = body_html.render(context)

	
			for email in email_list:
				email = EmailMultiAlternatives(subject, body_txt, 'Gulf Fishing Club <notifications@gccfishing.com>', [email])
				email.attach_alternative(body, "text/html")
				email.send()
		else:
			pass

	



post_save.connect(comment_notification_handler, sender = Comment, dispatch_uid='comment_posted_notification')

post_save.connect(send_emails, sender = Wallpost, dispatch_uid="new_post_notification")


admin.site.register(Wallpost)


admin.site.register(Comment)