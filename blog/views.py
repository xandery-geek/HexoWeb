from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.generic import View
from .models import Post, Category, Tag
from website.models import Website
from website.website_config import deploy_website
from PIL import Image
import uuid
import re
import yaml
import os


blog_template = {'title': None, 'date': None, 'tags': None, 'categories': None}


def create_article(filename, article):
    """ create article according to blog post
    :param filename: the article path(filename)
    :param article: the Post object
    :return:
    """
    try:
        with open(filename, 'w') as f:
            f.write('---\n')
            data = dict(blog_template)
            data['title'] = article.title
            data['date'] = article.update_time.astimezone(Post.cur_timezone).strftime('%Y-%m-%d %H:%M:%S')
            tag_list = [tag.name for tag in article.tags.all()]
            if tag_list:
                data['tags'] = tag_list

            if article.category:
                data['categories'] = article.category.name

            # output header
            yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False,
                           encoding='utf-8', allow_unicode=True)

        with open(filename, 'a') as f:
            content = article.content

            f.write('---\n')
            f.write(content)
            f.seek(0, 0)
    except FileNotFoundError:
        return False
    return True


def delete_article(filename):
    try:
        os.remove(filename)
    except FileNotFoundError:
        return False
    return True


def pack_post_list(post_list):
    data_list = []
    for post in post_list:
        update_time = post.update_time.astimezone(Post.cur_timezone).strftime(Post.time_format)
        data_list.append({
            'id': post.id,
            'title': post.title,
            'update_time': update_time})

    data = {'posts': data_list}
    return data


class PostView(View):
    get_method = ['all', 'draft', 'search']

    @method_decorator(login_required(login_url='/account/login/'))
    def get(self, request, **kwargs):
        user = request.user
        website = Website.get_current_website(user.id)
        if not website:
            return render(request, 'blog.html', {})

        try:
            option = kwargs['option']
            data = {}
            if option in PostView.get_method:
                handle = getattr(self, option)
                data = handle(website.id, **kwargs)
            return JsonResponse(data)
        except KeyError:
            context = self.get_default(website.id)

        return render(request, 'blog.html', context)

    @staticmethod
    def get_default(website_id):
        post_list = Post.get_by_website(website_id)

        first_post = None
        first_tags = None
        if post_list:
            first_post = post_list[0]
            first_tags = first_post.tags.all()

        category_list = Category.get_by_website(website_id)
        tag_list = Tag.get_by_website(website_id)

        context = {
            'posts': post_list,
            'cate': category_list,
            'tag': tag_list,
            'first': first_post,
            'first_tags': first_tags,
        }
        return context

    def all(self, website_id, **kwargs):
        post_list = Post.get_by_website(website_id)
        return pack_post_list(post_list)

    def draft(self, website_id, **kwargs):
        post_list = Post.objects.filter(website_id=website_id, status=Post.STATUS_DRAFT)
        return pack_post_list(post_list)

    def search(self, website_id, **kwargs):
        keyword = kwargs['keyword']
        post_list = Post.objects.filter(website_id=website_id, status=Post.STATUS_NORMAL)
        post_list = [post for post in post_list if re.search(keyword, post.title)]
        return pack_post_list(post_list)


class PostDetailView(View):
    @method_decorator(login_required(login_url='/account/login/'))
    def get(self, request, **kwargs):
        pk = kwargs['pk']

        user = request.user
        website = Website.get_current_website(user.id)
        if not website:
            return HttpResponseBadRequest()

        try:
            post = Post.objects.get(pk=pk, website=website)
            tags = post.tags.all()
            tags_name = [t.name for t in tags]
        except ObjectDoesNotExist:
            return HttpResponseBadRequest()

        update_time = post.update_time.astimezone(Post.cur_timezone).strftime(Post.time_format)
        context = {
            'post_title': post.title,
            'post_update': update_time,
            'post_content': post.content,
            'post_tags': tags_name,
        }

        return JsonResponse(context)


class CategoryTagView(View):
    post_method = ['create', 'delete']

    def __init__(self):
        super(CategoryTagView, self).__init__()
        self.website = None
        self.pk = None

    def get_attribute(self, request, **kwargs):
        try:
            self.pk = kwargs['pk']
        except KeyError:
            self.pk = None
        user = request.user
        self.website = Website.get_current_website(user.id)

    @method_decorator(login_required(login_url='/account/login/'))
    def get(self, request, **kwargs):
        self.get_attribute(request, **kwargs)
        posts_list = self.get_post_list()
        data = pack_post_list(posts_list)
        return JsonResponse(data)

    @method_decorator(login_required(login_url='/account/login/'))
    def post(self, request, **kwargs):
        self.get_attribute(request, **kwargs)
        option = kwargs['option']

        try:
            if option in CategoryTagView.post_method:
                handle = getattr(self, option)
                context = handle(request)
                return JsonResponse(context)
            else:
                return HttpResponseBadRequest()
        except ValueError:
            return HttpResponseBadRequest()

    def get_post_list(self):
        return []


class CategoryView(CategoryTagView):

    def get_post_list(self):
        if not self.website:
            return []
        post_list = Post.get_by_category(self.pk).filter(website=self.website)
        return post_list

    def create(self, request):
        if not self.website:
            raise ValueError('no website!')

        name = request.POST.get('name')
        if name == "":
            return {'tip': '分类名不能为空'}

        try:
            Category.objects.get(name=name, website=self.website)
        except ObjectDoesNotExist:
            cate = Category.objects.create(name=name, website=self.website)
            cate.save()
            return {}
        else:
            return {'tip': '分类已存在'}

    def delete(self, request):
        try:
            cate = Category.objects.get(pk=self.pk, website=self.website)
            cate.delete()
        except ObjectDoesNotExist:
            raise ValueError('no category whose primary key is {}'.format(self.pk))
        return {}


class TagView(CategoryTagView):
    def get_post_list(self):
        if not self.website:
            return []
        post_list = Post.get_by_tag(self.pk).filter(website=self.website)
        return post_list

    def create(self, request):
        if not self.website:
            raise ValueError('no website!')
        name = request.POST.get('name')
        if name == "":
            return {'tip': '标签名不能为空'}

        try:
            Tag.objects.get(name=name, website=self.website)
        except ObjectDoesNotExist:
            tag = Tag.objects.create(name=name, website=self.website)
            tag.save()
            return {}
        else:
            return {'tip': '标签已存在'}

    def delete(self, request):
        try:
            tag = Tag.objects.get(pk=self.pk, website=self.website)
            tag.delete()
        except ObjectDoesNotExist:
            raise ValueError('no tag whose primary key is {}'.format(self.pk))
        return {}


class PostOperateView(View):
    get_method = ['new', 'edit']
    post_method = ['update', 'save', 'delete', 'release']

    def __init__(self):
        super().__init__()
        self.pk = None
        self.website = None

    def get_attribute(self, request, **kwargs):
        try:
            self.pk = kwargs['pk']
        except KeyError:
            self.pk = None
        user = request.user
        self.website = Website.get_current_website(user.id)

    @method_decorator(login_required(login_url='/account/login/'))
    def get(self, request, **kwargs):
        self.get_attribute(request, **kwargs)
        try:
            option = kwargs['option']
        except KeyError:
            option = 'new'

        try:
            if option in PostOperateView.get_method:
                handler = getattr(self, option)
                context = handler()
                return render(request, 'editor.html', context)
            else:
                return HttpResponseBadRequest()
        except ValueError:
            return HttpResponseBadRequest()

    def get_category_tag(self):
        cate_list = Category.get_by_website(self.website.id)
        tag_list = Tag.get_by_website(self.website.id)
        context = {
            'cate_list': cate_list,
            'tag_list': tag_list,
        }

        return context

    def new(self):
        context = self.get_category_tag()
        context.update({
            'id': 0,
        })
        return context

    def edit(self):
        context = self.get_category_tag()
        try:
            post = Post.objects.get(pk=self.pk, website=self.website)

            title = post.title
            content = post.content
            status = post.status
            cate = post.category
            tag = post.tags.all()

        except ObjectDoesNotExist:
            raise ValueError('no blog whose primary key is {}'.format(self.pk))

        context.update({
            'id': post.id,
            'title': title,
            'content': content,
            'status': status,
            'cate': cate,
            'tag': tag
        })

        return context

    @method_decorator(login_required(login_url='/account/login/'))
    def post(self, request, **kwargs):
        self.get_attribute(request, **kwargs)
        option = kwargs['option']

        try:
            if option in PostOperateView.post_method:
                handler = getattr(self, option)
                context = handler(request)
                return JsonResponse(context)
            else:
                return HttpResponseBadRequest()
        except ValueError:
            return HttpResponseBadRequest()

    def create(self, title):
        """
        create blog article, the status of article is draft
        :return:
        """
        if not self.website:
            raise ValueError('no website！')

        if title is None or title == '':
            return None

        blog_post = Post.objects.create(title=title, content='', website=self.website)
        post_filename = "%04d.md" % blog_post.id
        blog_post.relative_path = os.path.join('source/_posts', post_filename)
        blog_post.status = Post.STATUS_DRAFT
        return blog_post

    def release(self, request):
        blog_post = self.get_post([Post.STATUS_NORMAL, Post.STATUS_DRAFT])
        if blog_post is None:
            return {'tip': '发布失败！'}

        self.save(request, blog_post)
        if blog_post.changed:
            blog_post.status = Post.STATUS_NORMAL
            blog_post.changed = False
            blog_post.save()
            delete_article(blog_post.path)
            if not create_article(blog_post.path, blog_post):
                return {'tip': '发布失败'}
        else:
            return {'tip': '文章未修改'}
        return {}

    def update(self, request):
        """
        更新所有修改了的博客
        :return:
        """
        post_list = Post.objects.filter(website=self.website, status=Post.STATUS_NORMAL, changed=True)
        for post in post_list:
            post.changed = False
            post.save()
            delete_article(post.path)
            create_article(post.path, post)

        if deploy_website(self.website):
            return {'tip': '发布成功'}
        else:
            return {'tip': '发布失败'}

    def save(self, request, blog_post=None):
        context = {}
        if blog_post is None:
            blog_post = self.get_post([Post.STATUS_NORMAL, Post.STATUS_DRAFT])

        title = request.POST.get('title')
        if blog_post is None:
            if title is None or title == '':
                return {'tip': '文章标题不能为空！'}

            blog_post = self.create(request)
            context.update({'id': blog_post.id})

        status = request.POST.get('status')
        content = request.POST.get('content')
        tag_list = request.POST.get('tag')
        category = request.POST.get('category')

        if status is not None and status == 'draft':
            blog_post.status = Post.STATUS_DRAFT

        if title is not None:
            if title == '':
                return {'tip': '文章标题不能为空！'}
            blog_post.title = title

        if content is not None:
            blog_post.content = content

        old_cate = None
        old_tags = []
        try:
            if category is not None:
                if category == '':
                    blog_post.category = None
                else:
                    cate = Category.objects.get(name=category, website=self.website)
                    old_cate = blog_post.update_category(cate)

            if tag_list is not None:
                tag_list = tag_list.split(',')
                tags = Tag.objects.filter(name__in=tag_list, website=self.website)
                old_tags = blog_post.update_tags(tags, website=self.website)
        except ObjectDoesNotExist:
            return {'tip': '分类或者标签不存在，请先创建！'}

        if title or status or content or tag_list or category:
            blog_post.changed = True
            blog_post.save()

            # auto delete category and tag which is not relied on
            Category.auto_delete(old_cate)
            Tag.auto_delete(old_tags)

        return context

    def delete(self, request):
        blog_post = self.get_post([Post.STATUS_NORMAL, Post.STATUS_DRAFT])

        if blog_post is None:
            raise ValueError('blog is not exist!')

        if blog_post.status == Post.STATUS_NORMAL:
            delete_article(blog_post.path)

        tag_list = blog_post.tags.all()
        cate = blog_post.category
        blog_post.delete()

        Tag.auto_delete(tag_list)
        Category.auto_delete(cate)

        return {'url': reverse('blog')}

    def get_post(self, status=Post.STATUS_NORMAL):
        if not self.website:
            return None
        if not isinstance(status, list):
            status = [status]

        try:
            return Post.objects.get(pk=self.pk, website=self.website, status__in=status)
        except ObjectDoesNotExist:
            return None
