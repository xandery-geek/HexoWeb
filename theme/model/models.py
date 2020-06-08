from django.db.models import ObjectDoesNotExist
from website.models import Website
from django.db import models
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
THEME_RELATIVE_PATH = 'template/theme/'


class TemplateTheme(models.Model):
    # user can not change these fields
    name = models.CharField(max_length=64, blank=False, verbose_name='name')
    desc = models.TextField(max_length=1024, blank=False, verbose_name='description')
    tags = models.CharField(max_length=128, blank=False, verbose_name='tags')
    preview = models.ImageField(blank=True, upload_to='theme', verbose_name="preview")
    preview_url = models.URLField(blank=True, null=True, verbose_name='preview url')
    relative_path = models.CharField(max_length=128, blank=True, verbose_name='theme relative path')

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        path = os.path.join(THEME_RELATIVE_PATH, self.name)
        self.relative_path = path
        super().save(force_insert, force_update, using, update_fields)

    def get_theme_abspath(self):
        return os.path.join(BASE_DIR, self.relative_path)


class BaseTheme(models.Model):
    template = models.ForeignKey(to=TemplateTheme, blank=False, null=True, on_delete=models.SET_NULL)
    website = models.ForeignKey(to=Website, blank=False, null=True, on_delete=models.SET_NULL)
    relative_path = models.CharField(max_length=128, blank=True, verbose_name='theme relative path')

    @classmethod
    def get_by_website(cls, website):
        try:
            return cls.objects.get(website=website)
        except ObjectDoesNotExist:
            return None

    def get_theme_abspath(self):
        website = self.website
        return os.path.join(website.path, self.relative_path)

    def delete(self, using=None, keep_parents=False):
        abs_path = self.get_theme_abspath()
        if os.path.exists(abs_path):
            os.rmdir(abs_path)
        super(BaseTheme, self).delete(using, keep_parents)
