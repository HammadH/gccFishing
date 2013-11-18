from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string

User = get_user_model()

sender = 'support@greatwhitestudios.com'

test_user = User.objects.get(email='wishmecake@gmail.com')

email_subject = render_to_string('Email_notification_newFeatures_subject.txt')
email_body = render_to_string('Email_notification.html', {'user':test_user})
if send_mail(email_subject, email_body, sender, [test_user.email], fail_silently=False):
	print 'email sent'
else:
	print 'email sending crashed'

