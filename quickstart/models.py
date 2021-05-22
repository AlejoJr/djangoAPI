from django.db import models
from jsonfield import JSONField


# Create your models here.
class Lyric(models.Model):
    lyric = models.TextField(null=True,
                             default=None)
    artist = models.CharField(max_length=100,
                              null=True,
                              default=None)
    title = models.CharField(max_length=200,
                             null=True,
                             default=None)
    score = models.CharField(max_length=100,
                             null=True,
                             default=None)
    feeling = models.CharField(max_length=100,
                             null=True,
                             default=None)








