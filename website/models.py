from django.db import models
from user.models import User
from .website_config import change_theme


# Create your models here.
class Website(models.Model):
    STATUS_UNRELEASED = 0
    STATUS_NORMAL = 1

    STATUS_ITEMS = (
        (STATUS_UNRELEASED, 'unreleased'),
        (STATUS_NORMAL, 'normal'),
    )

    LANGUAGE_EN = 0
    LANGUAGE_ZH = 1

    LANGUAGE_ITEMS = (
        (LANGUAGE_EN, 'en'),
        (LANGUAGE_ZH, 'zh-CN'),
    )

    DEFAULT_THEME = 'landscape'

    status = models.PositiveIntegerField(default=STATUS_NORMAL, choices=STATUS_ITEMS, verbose_name="website status")

    title = models.CharField(max_length=64, blank=False, verbose_name='title')
    subtitle = models.CharField(max_length=128, blank=True, verbose_name='subtitle')
    desc = models.TextField(max_length=128, blank=True, verbose_name='description')
    keyword = models.CharField(max_length=128, blank=True, verbose_name='keyword')
    author = models.CharField(max_length=64, blank=False, verbose_name='author')
    language = models.PositiveIntegerField(default=LANGUAGE_EN, choices=LANGUAGE_ITEMS, verbose_name="website language")
    url = models.URLField(verbose_name='url', blank=False)
    per_page = models.IntegerField(default=6, blank=False, verbose_name='article in per page')
    theme = models.CharField(max_length=1024, default='', blank=True, null=True, verbose_name='website theme name list')
    cur_theme = models.CharField(max_length=32, default=DEFAULT_THEME, blank=True, null=True,
                                 verbose_name='website current theme name')

    repository = models.CharField(max_length=64, blank=False, verbose_name='git repository')
    branch = models.CharField(max_length=64, default='master', blank=False, verbose_name="git branch")
    git_username = models.CharField(max_length=64, blank=False, verbose_name='git username')
    git_email = models.EmailField(max_length=64, blank=False, default='eamil@gmail.com', verbose_name='git email')
    git_password = models.CharField(max_length=64, blank=False, verbose_name='git password')

    owner = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name='website owner')
    path = models.CharField(max_length=128, default='', blank=False, verbose_name='website path')
    creat_time = models.DateTimeField(auto_now_add=True, verbose_name="create time")

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title

    @classmethod
    def get_by_owner(cls, owner_id):
        try:
            owner = User.objects.get(id=owner_id)
        except User.DoesNotExist:
            website_list = []
        else:
            website_list = cls.objects.filter(owner=owner, status=Website.STATUS_NORMAL)

        return website_list

    @classmethod
    def get_current_website(cls, owner_id):
        website_list = cls.get_by_owner(owner_id)
        if website_list:
            return website_list[0]
        return None

    def add_theme(self, name):
        theme_list = self.get_theme_list()
        if name in theme_list or name == self.cur_theme:
            return False

        if self.cur_theme != '':
            theme_list.append(self.cur_theme)
            self.theme = ' '.join(theme_list)

        self.cur_theme = name
        self.update_theme(self.cur_theme)
        return True

    def update_theme(self, theme):
        change_theme(self.path, theme)

    def delete_theme(self, name):
        theme_list = self.get_theme_list()
        if name in theme_list:
            theme_list.remove(name)
            self.theme = ' '.join(theme_list)

    def get_theme_list(self):
        theme = self.theme
        if theme is None or theme == '':
            return []
        return theme.split(' ')
