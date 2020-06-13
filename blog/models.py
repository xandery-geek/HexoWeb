from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from website.models import Website
from django.utils import timezone
import pytz
import os


class Category(models.Model):
    STATUS_DELETE = 0
    STATUS_NORMAL = 1

    STATUS_ITEMS = (
        (STATUS_DELETE, 'deleted'),
        (STATUS_NORMAL, 'normal'),
    )

    name = models.CharField(max_length=50, verbose_name="name")
    status = models.PositiveIntegerField(default=STATUS_NORMAL, choices=STATUS_ITEMS, verbose_name="status")
    creat_time = models.DateTimeField(auto_now_add=True, verbose_name="create time")
    website = models.ForeignKey(Website, on_delete=models.CASCADE, verbose_name='website')

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    @classmethod
    def get_by_website(cls, website_id):
        try:
            website = Website.objects.get(id=website_id)
        except ObjectDoesNotExist:
            category_list = []
        else:
            category_list = cls.objects.filter(website=website, status=Category.STATUS_NORMAL)

        return category_list

    @classmethod
    def auto_delete(cls, cate):
        if cate is None:
            return
        count = Post.objects.filter(category=cate).count()
        # database has not been updated now, so the count is one but not zero.
        if count == 1:
            cate.delete()


class Tag(models.Model):
    STATUS_DELETE = 0
    STATUS_NORMAL = 1

    STATUS_ITEMS = (
        (STATUS_DELETE, 'deleted'),
        (STATUS_NORMAL, 'normal'),
    )

    name = models.CharField(max_length=50, verbose_name="name")
    status = models.PositiveIntegerField(default=STATUS_NORMAL, choices=STATUS_ITEMS, verbose_name='status')
    website = models.ForeignKey(Website, on_delete=models.CASCADE, verbose_name='website')
    creat_time = models.DateTimeField(auto_now_add=True, verbose_name="create time")

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    @classmethod
    def get_by_website(cls, website_id):
        try:
            website = Website.objects.get(id=website_id)
        except ObjectDoesNotExist:
            tags_list = []
        else:
            tags_list = cls.objects.filter(website=website, status=Tag.STATUS_NORMAL)

        return tags_list

    @classmethod
    def auto_delete(cls, tag_list):
        for tag in tag_list:
            count = Post.objects.filter(tags__in=tag).count()

            # database has not been updated now, so the count is one but not zero.
            if count == 1:
                tag.delete()


class Post(models.Model):
    STATUS_DELETE = 0
    STATUS_NORMAL = 1
    STATUS_DRAFT = 2

    STATUS_ITEMS = (
        (STATUS_DELETE, 'deleted'),
        (STATUS_NORMAL, 'normal'),
        (STATUS_DRAFT, 'draft'),
    )

    title = models.CharField(max_length=256, verbose_name="title")
    content = models.TextField(verbose_name="content")
    relative_path = models.CharField(max_length=32, default=None, blank=False, null=True, verbose_name="path")
    status = models.PositiveIntegerField(default=STATUS_NORMAL, choices=STATUS_ITEMS, verbose_name="status")
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="category")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="tag")
    website = models.ForeignKey(Website, on_delete=models.CASCADE, verbose_name='website')
    changed = models.BooleanField(default=False, blank=False, verbose_name='post changed')
    creat_time = models.DateTimeField(auto_now_add=True, verbose_name="create time")
    update_time = models.DateTimeField(auto_now_add=True, verbose_name="update time")

    cur_timezone = pytz.timezone('Asia/Shanghai')
    time_format = '%b %d, %Y, %I:%M %p'

    class Meta:
        ordering = ['-update_time']  # 根据update_time降序排序

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title

    def update_category(self, cate):
        if self.category != cate:
            # remove category when no posts rely on it
            old_cate = self.category
            self.category = cate
            Category.auto_delete(old_cate)

    def update_tags(self, tag_list, website):
        new_set = set(tag_list)
        old_set = set(self.tags.filter(website=website))
        removed = old_set - new_set
        added = new_set - old_set
        self.tags.remove(*list(removed))
        self.tags.add(*list(added))  # 将列表分解为独立的参数

        # remove tag when no posts rely on it
        Tag.auto_delete(list(removed))

    @classmethod
    def get_by_website(cls, website_id):
        post_list = cls.objects.filter(website_id=website_id, status=Post.STATUS_NORMAL)
        return post_list

    @classmethod
    def get_by_tag(cls, tag_id):
        tag_id_list = [tag_id]
        post_list = cls.objects.filter(tags__in=tag_id_list, status=Post.STATUS_NORMAL)
        return post_list

    @classmethod
    def get_by_category(cls, category_id):
        post_list = cls.objects.filter(category_id=category_id, status=Post.STATUS_NORMAL)
        return post_list

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.update_time = timezone.now()
        super().save(force_insert, force_update, using, update_fields)

    @property
    def path(self):
        return os.path.join(self.website.path, self.relative_path)
