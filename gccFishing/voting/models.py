from datetime import datetime
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from wall.models import Wallpost


User = get_user_model()

try:
    from django.utils.timezone import now
except ImportError:
    now = datetime.now

from voting.managers import VoteManager


SCORES = (
    (+1, u'+1'),
    (-1, u'-1'),
)


class Vote(models.Model):
    """
    A vote on an object by a User.
    """
    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object = generic.GenericForeignKey('content_type', 'object_id')
    vote = models.SmallIntegerField(choices=SCORES)
    time_stamp = models.DateTimeField(editable=False, default=now)

    objects = VoteManager()

    class Meta:
        db_table = 'votes'
        # One vote per user per object
        unique_together = (('user', 'content_type', 'object_id'),)

    def __unicode__(self):
        return u'%s: %s on %s' % (self.user, self.vote, self.object)

    def is_upvote(self):
        return self.vote == 1

    def is_downvote(self):
        return self.vote == -1


def update_user_reputation(sender, instance, created,  **kwargs):
    post = Wallpost.objects.get(id=instance.object_id)
    user = post.author
    if instance.vote == 1:
        user.reputation += 10
    elif instance.vote == -1:
        user.reputation -= 10
    user.save()
    return




post_save.connect(update_user_reputation, sender=Vote, dispatch_uid='vote_created')
