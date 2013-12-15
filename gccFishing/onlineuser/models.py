from  datetime  import datetime, timedelta
from django.utils.timezone import utc
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from Locations.models import City
User = get_user_model()

last_online_duration = getattr(settings, 'LAST_ONLINE_DURATION', 90)

class OnlineManager(models.Manager):
    def onlines(self):
        now = datetime.now()
        return Online.objects.filter(\
                updated_on__gte = now - timedelta(seconds = last_online_duration)\
                )

    def online_users(self, city_slug):
        return self.onlines().filter(user__isnull=False, user__city__slug=city_slug).count()

    def last_seen(self, user):
        return Online.objects.get(user__isnull=False, user=user).updated_on


class Online(models.Model):
    user = models.OneToOneField(User, related_name='online', blank=True, null=True)
    ident = models.CharField(max_length=200, unique=True)#username id for user / ip for guest
    session_key = models.CharField(max_length=64)
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    objects = OnlineManager()

    def __unicode__(self):
        return self.ident

    def username(self):
        return self.ident.split(' ')[0]

    def user_id(self):
        ident = self.ident.split(' ')
        if len(ident)>2:
            return ident[1]
        return ''

    def online(self):
        now = datetime.utcnow().replace(tzinfo=utc)
        if (now - self.updated_on).seconds < last_online_duration:
            return True
        return False   

    def save(self, *args, **kwargs):
        if self.user:
            self.ident = '%s %s' % (self.user.email, self.user.pk)
        super(Online, self).save(*args, **kwargs)

def getOnlineInfos(detail=False):
    total_onlines = Online.objects.onlines().count()
    total_onlines_user = Online.objects.online_users().count()
    total_onlines_guest = total_onlines - total_onlines_user
    ctx = {'total_onlines': total_onlines, 'total_onlines_user': total_onlines_user, \
            'total_onlines_guest': total_onlines_guest}
    if detail:
        ctx['online_users'] = Online.objects.online_users()
    return ctx
