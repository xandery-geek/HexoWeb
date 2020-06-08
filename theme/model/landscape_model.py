from django.db.models import ObjectDoesNotExist
from django.db import models
from .models import BaseTheme, TemplateTheme
from .utility import covert_image_format
import uuid
import os


class LandscapeTheme(BaseTheme):
    SIDEBAR_LEFT = 0
    SIDEBAR_RIGHT = 1
    SIDEBAR_BOTTOM = 2

    SIDEBAR_ITEMS = (
        (SIDEBAR_LEFT, 'left'),
        (SIDEBAR_RIGHT, 'right'),
        (SIDEBAR_BOTTOM, 'bottom'),
    )

    # each bit in self.widgets present a widget
    WIDGETS_ITEMS = (
        (0, 'category'),
        (1, 'tag'),
        (2, 'tagcloud'),
        (3, 'archive'),
        (4, 'recent_posts'),
    )

    favicon = models.ImageField(upload_to='customise_theme', blank=True,
                                verbose_name='favourite icon showed in browser title')
    banner = models.ImageField(upload_to='customise_theme', blank=True,
                               verbose_name='background image of landscape showed in post header')
    # content
    excerpt_link = models.CharField(default="Read More", max_length=32, blank=False,
                                    verbose_name='tip for button of read more')

    # sidebar
    position = models.PositiveIntegerField(default=SIDEBAR_LEFT, choices=SIDEBAR_ITEMS, blank=False,
                                           verbose_name='the position of sidebar')
    widgets = models.PositiveIntegerField(default=0x1F, blank=False, verbose_name='widgets showed in sidebar')
    show_count = models.BooleanField(default=True, blank=False, verbose_name='show post count in sidebar')

    def __init__(self, *args, **kwargs):
        super(LandscapeTheme, self).__init__(*args, **kwargs)
        try:
            template = TemplateTheme.objects.get(name='landscape')
        except ObjectDoesNotExist:
            raise ValueError("theme 'landscape' not exist!")

        self.template = template
        path = os.path.join('themes', self.template.name)
        self.relative_path = path

    def set_widgets(self, selected_list):
        widgets = 0
        for i in selected_list:
            widgets = widgets | (1 << i)

        self.widgets = widgets

    def get_widgets_content(self):
        widgets = []

        for i, w in LandscapeTheme.WIDGETS_ITEMS:
            if self.widgets & (1 << i) != 0:
                widgets.append(w)

        return widgets

    def get_position_content(self):
        return LandscapeTheme.SIDEBAR_ITEMS[self.position][1]

    def get_widgets_no(self):
        widgets = []

        for i in range(len(LandscapeTheme.WIDGETS_ITEMS)):
            if (self.widgets & (1 << i)) != 0:
                widgets.append(i)

        return widgets

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        cp_favicon = False
        cp_banner = False
        try:
            old_instance = LandscapeTheme.objects.get(pk=self.id)
            if old_instance.favicon != self.favicon:
                cp_favicon = True
                try:
                    file = old_instance.favicon.path
                    if os.path.isfile(file):
                        os.remove(file)
                    # convert image format
                    slug = '%04d' % (self.id,)
                    filename = '{0}{1}.png'.format(slug, str(uuid.uuid4())[-5:])
                    covert_image_format(self.favicon, filename, 'PNG')
                except ValueError:
                    pass

            if old_instance.banner != self.banner:
                cp_banner = True
                try:
                    file = old_instance.banner.path
                    if os.path.isfile(file):
                        os.remove(file)
                    # convert image format
                    slug = '%04d' % (self.id,)
                    filename = '{0}{1}.jpg'.format(slug, str(uuid.uuid4())[-5:])
                    covert_image_format(self.banner, filename, 'JPEG')
                except ValueError:
                    pass
        except ObjectDoesNotExist:
            pass

        super(LandscapeTheme, self).save(force_insert, force_update, using, update_fields)

        # cp favicon to directory
        if cp_favicon:
            favicon_path = os.path.join(self.get_theme_abspath(), '../../source/img/favicon.png')
            command = "cp {} {}".format(self.favicon.path, favicon_path)
            os.system(command)

        # cp banner to directory
        if cp_banner:
            banner_path = os.path.join(self.get_theme_abspath(), 'source/css/images/banner.jpg')
            command = "cp {} {}".format(self.banner.path, banner_path)
            os.system(command)

    def delete(self, using=None, keep_parents=False):
        if os.path.isfile(self.favicon.path):
            os.remove(self.favicon.path)
        if os.path.isfile(self.banner.path):
            os.remove(self.banner.path)

        super(LandscapeTheme, self).delete(using, keep_parents)
