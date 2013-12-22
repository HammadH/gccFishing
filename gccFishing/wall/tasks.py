from __future__ import absolute_import

from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.db.models.loading import get_model
from django.template.loader import Context, render_to_string, get_template

from django.core.mail import EmailMultiAlternatives
from Locations.models import City



User = get_user_model()

from celery import shared_task





def send_emails_delegate(sender, instance, created, **kwargs):  
	sender = sender
	instance = instance 
	created = created

	send_emails.delay(sender, instance, created)
	
	

@shared_task
def send_emails(sender, instance, created, **kwargs):
	if created:
		author = getattr(instance, 'author')
		city = getattr(instance, 'city')
		email_list = []
		users = User.objects.filter(city=city, email_notification=1).exclude(id=author.id)
		for user in users:
			if user.is_active == True:
			#	if user.online.online() == False:
				email_list.append(user.email)
			#	else:
			#		pass
			else:
				pass	
							

		context = Context()
		context['post'] = instance
		context['author'] = author
		context['city'] = city
			
		subject = getattr(instance, 'text')
		
		if '\n' in subject:
			return
		
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
		
		return
	
	else:
		pass



post_save.connect(send_emails_delegate, sender = get_model('wall','Wallpost'), weak = False, dispatch_uid = "new_post_notification" )




