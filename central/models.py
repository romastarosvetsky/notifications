from django.contrib.gis.db.models import GeometryField
from django.db import models

from authentication.models import User


class Notification(models.Model):

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    owner = models.ForeignKey(User, verbose_name='Owner', on_delete=models.CASCADE, null=False, blank=False,
                              related_name='owner')
    title = models.CharField(verbose_name='Title', max_length=128, blank=True, null=True)
    description = models.TextField(verbose_name='Description', blank=True, null=True)
    place = GeometryField(verbose_name='Place', geography=True, blank=True, null=True)
    participants = models.ManyToManyField(User, verbose_name='Participants', related_name='participants',
                                          blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='Created at', auto_now_add=True)
    activation_time = models.DateTimeField(verbose_name='Activation time', blank=False, null=False)
    sent = models.BooleanField(verbose_name='Has been sent', default=False)
