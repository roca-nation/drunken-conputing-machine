from django.db import models
from django.utils import timezone
import datetime

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    def __unicode__(self):
        return self.name

class Page(models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)
    pub_date = models.DateTimeField('date published')
    def was_published_recently(self):
        return self.pub_date >= timezone.now() -datetime.timedelta(days=1)

    def __unicode__(self):
        return self.title

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'









