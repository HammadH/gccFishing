
from __future__ import unicode_literals

import logging


import datetime
import hashlib
import random
import re
from collections import defaultdict

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import BaseUserManager

from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from sorl.thumbnail import ImageField

from django.db.models.signals import post_save

from django.core.urlresolvers import reverse

SHA1_RE = re.compile('^[a-f0-9]{40}$')


try:
    from django.utils.timezone import now as datetime_now
except ImportError:
    datetime_now = datetime.datetime.now


def image_path(instance, filename):
    path = "Images/%s"	%filename
    return path 

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):

        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.name = kwargs['name']
        user.image = kwargs['image']
        user.country = kwargs['country']
        user.city = kwargs['city']

        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        username = kwargs['name']	
        if isinstance(username, unicode):
            username = username.encode('utf-8')
        user.activation_key = hashlib.sha1(salt+username).hexdigest()

            
        user.save(using=self._db)

        user.send_activation_email(email)
        return user

    def create_superuser(self, **kwargs):
        user = self.create_user(**kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user




class AbstractEmailUser(AbstractBaseUser, PermissionsMixin):
   


    ACTIVATED = u"ALREADY_ACTIVATED"	

    email = models.EmailField(_('email address'), max_length=255, unique=True,
                              db_index=True,)

    
    activation_key = models.CharField(_('activation_key'), max_length = 40)		

    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=False,
        help_text=_('Designates whether this user should be treated as '
                    'active.  Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        abstract = True
        ordering = ['email']

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def send_activation_email(self, email):	
	email = email	
	ctx_dict = { 'activation_key' : self.activation_key,
		     'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
		                                                        }

	subject = render_to_string('activation_email_subject.txt', ctx_dict)
	subject = ''.join(subject.splitlines())
	message = render_to_string('activation_email.txt', ctx_dict)
		
	send_mail(subject, message, 'gccFishing.com', [email,],  fail_silently = False)
	
	

    def activation_key_expired(self):
	expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
		
	
	return self.activation_key == self.ACTIVATED or \
	(self.date_joined + expiration_date <= datetime_now())
    activation_key_expired.boolean = True

    
    def activate(self, activation_key):
        if SHA1_RE.search(activation_key):
	       try:
                self.get(activation_key = activation_key)
	       except:
                self.model.DoesNotExist
                return False
	       if not self.activation_key_expired():
                self.is_active = True
                self.activation_key = self.model.ACTIVATED
                self.save()
                return self
        return False


	#TODO = deleteExpiredUsers()

@python_2_unicode_compatible
class AbstractNamedUser(AbstractEmailUser):
    
    name = models.CharField(_('name'), max_length=255)
    
    image = ImageField(_('profile_image'), upload_to=image_path, default = settings.DEFAULT_IMAGE_PATH)
    
    country = models.ForeignKey('Locations.Country', related_name = "members", null = True)
    city = models.ForeignKey('Locations.City', related_name = "members", null = True)

    
    
	
    reputation = models.IntegerField(_("reputation"), default = 0)

    

    REQUIRED_FIELDS = ['name', 'image', 'country', 'city']

    class Meta:
        abstract = True
        ordering = ['name', 'email']

    def __str__(self):
        return '{name} <{email}>'.format(
            name=self.name,
            email=self.email,
        )

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name


    def get_absolute_url(self):
        return reverse('views.profile', args=[self.id])

    

   

class User(AbstractNamedUser):



    class Meta(AbstractNamedUser.Meta):
        swappable = 'AUTH_USER_MODEL'
        verbose_name = _('user')
        verbose_name_plural = _('users')


