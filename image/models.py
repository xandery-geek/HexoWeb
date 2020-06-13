from django.db import models
from user.models import User
import os


def upload_to(instance, filename):
    return os.path.join('photo', instance.owner.photo_relative_path, filename)


# Create your models here.
class ImageModel(models.Model):
    img = models.ImageField(upload_to=upload_to, blank=False, null=True, verbose_name='image')
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return self.img.name

    def __unicode__(self):
        return self.img.name

    def abs_url(self, request_url):
        url = request_url.split('//')[1]
        url = url.split('/')[0]
        url = 'http://' + url + self.img.url
        return url

    def delete(self, using=None, keep_parents=False):
        if os.path.exists(self.img.path):
            os.remove(self.img.path)

        super(ImageModel, self).delete(using, keep_parents)

    @classmethod
    def get_by_owner(cls, owner):
        image_list = cls.objects.filter(owner=owner)
        return image_list
