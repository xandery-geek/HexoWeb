from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, FileResponse, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy
from django.views.generic import View, FormView
from .forms import WebsiteForm
from .models import Website
from theme.view.views import get_theme_model
from theme.view.views import create_default_theme
from .website_config import *
import os


class WebsiteView(View):
    template_name = 'website.html'

    @method_decorator(login_required(login_url='/account/login/'))
    def get(self, request):
        user = request.user
        website_list = Website.get_by_owner(user.id)
        website_list = website_list.filter(status=Website.STATUS_NORMAL)

        context = {
            'count': website_list.count(),
            'websites': website_list
        }

        return render(request, WebsiteView.template_name, context)


class WebsiteDetailView(View):
    template_name = 'website_detail.html'

    @method_decorator(login_required(login_url='/account/login/'))
    def get(self, request, **kwargs):
        pk = kwargs['pk']
        user = request.user
        website_list = Website.get_by_owner(user.id)
        try:
            website = website_list.get(pk=pk, status=Website.STATUS_NORMAL)

            theme_list = []
            name_list = website.get_theme_list()
            for name in name_list:
                model = get_theme_model(name)
                if model is None:
                    continue
                theme = model.get_by_website(website)
                if theme:
                    theme_list.append(theme)

            model = get_theme_model(website.cur_theme)
            if model is None:
                return HttpResponseBadRequest()
            cur_theme = model.get_by_website(website)

            context = {
                'website': website,
                'themes': theme_list,
                'cur_theme': cur_theme
            }

        except ObjectDoesNotExist:
            return HttpResponseBadRequest()

        return render(request, WebsiteDetailView.template_name, context)


class CreateWebsiteView(FormView):
    form_class = WebsiteForm
    success_url = reverse_lazy('website')
    template_name = 'website_new.html'

    @method_decorator(login_required(login_url='/account/login/'))
    def get(self, request, *args, **kwargs):
        return render(request, CreateWebsiteView.template_name, {})

    @method_decorator(login_required(login_url='/account/login/'))
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            website = form.save(False)
            website.owner = request.user
            website.save()
            website.path = get_website_dir(request.user.id, website.id)
            website.save()
            if create_website(website.path) \
                    and update_website_config(website.path, website) \
                    and create_default_theme(website, website.cur_theme):

                return self.form_valid(form)

            # if create website failed, delete the website
            delete_website(website.path)
            website.delete()

        return self.form_invalid(form)

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        context.update({
            "tip": True,
            "title": "创建网站失败",
            "content": "",
        })

        return self.render_to_response(context)


class DeleteWebsiteView(View):
    success_url = reverse_lazy('website')

    @method_decorator(login_required(login_url='/account/login/'))
    def post(self, request, *args, **kwargs):
        try:
            pk = request.POST.get('id')
            email = request.POST.get('email')
            if email == request.user.email:
                website = Website.get_by_owner(request.user.id).get(pk=pk)
                delete_website(website.path)
                website.delete()
            else:
                return JsonResponse({'error': '用户名不正确!'})
        except KeyError:
            return HttpResponseBadRequest()
        except ObjectDoesNotExist:
            return HttpResponseBadRequest()

        return JsonResponse({'url': DeleteWebsiteView.success_url})


class UpdateWebsiteView(View):
    get_method = ['basic', 'deploy']
    post_method = ['basic', 'deploy']

    def __init__(self):
        super().__init__()
        self.website = None

    def get_attribute(self, request, **kwargs):
        pk = kwargs['pk']
        try:
            self.website = Website.objects.get(pk=pk, owner=request.user)
        except ObjectDoesNotExist:
            self.website = None

    @method_decorator(login_required(login_url='/account/login/'))
    def get(self, request, **kwargs):
        self.get_attribute(request, **kwargs)
        if self.website is None:
            return redirect('website')

        option = kwargs['option']

        context = {}
        if option in UpdateWebsiteView.get_method:
            handle = getattr(self, 'get_' + option)
            context = handle()

        return render(request, 'website_update.html', context)

    def get_basic(self):
        context = {
            'type': 0,
            'id': self.website.id,
            'header': '修改网站基本信息',
            'title': self.website.title,
            'subtitle': self.website.subtitle,
            'desc': self.website.desc,
            'keyword': self.website.keyword,
            'author': self.website.author,
            'per_page': self.website.per_page
        }

        return context

    def get_deploy(self):
        context = {
            'id': self.website.id,
            'type': 1,
            'header': '修改网站部署信息',
            'url': self.website.url,
            'repository': self.website.repository,
            'branch': self.website.branch,
            'git_username': self.website.git_username,
            'git_password': '******',
        }

        return context

    @method_decorator(login_required(login_url='/account/login/'))
    def post(self, request, **kwargs):
        self.get_attribute(request, **kwargs)
        if self.website is None:
            return redirect('website')

        option = kwargs['option']

        context = {}
        status = False
        if option in UpdateWebsiteView.get_method:
            handle = getattr(self, 'post_' + option)
            status, context = handle(request)
        if status:
            return redirect('website_detail', str(self.website.id))
        else:
            return render(request, 'website_update.html', context)

    def post_basic(self, request):
        website = self.website

        title = request.POST.get('title')
        subtitle = request.POST.get('subtitle')
        desc = request.POST.get('desc')
        keyword = request.POST.get('keyword')
        author = request.POST.get('author')
        per_page = request.POST.get('per_page')

        try:
            per_page = int(per_page)
            if per_page <= 0:
                return False, {'tip': 'Per Page 必须为大于0的数字'}

            website.title = title
            website.subtitle = subtitle
            website.desc = desc
            website.keyword = keyword
            website.author = author
            website.per_page = per_page
            website.save()
            self.update_config()
        except:
            return False, {'tip': '表单填写不正确'}

        return True, {}

    def post_deploy(self, request):
        website = self.website

        url = request.POST.get('url')
        repository = request.POST.get('repository')
        branch = request.POST.get('branch')
        git_username = request.POST.get('git_username')
        git_password = request.POST.get('git_password')

        try:
            website.url = url
            website.repository = repository
            website.branch = branch
            website.git_username = git_username
            website.git_password = git_password
            website.save()
            self.update_config()
        except:
            return False, {'tip': '表单填写不正确'}

        return True, {}

    def update_config(self):
        update_website_config(self.website.path, self.website)
        deploy_website(self.website.path)


class ExportWebsiteView(View):
    def get(self, request, **kwargs):
        pk = kwargs['pk']
        user = request.user
        try:
            website = Website.objects.get(pk=pk, owner=user)
        except ObjectDoesNotExist:
            return HttpResponse(status=204)

        option = kwargs['option']
        if option == 'markdown':
            return self.export_markdown(website)
        elif option == 'hexo':
            return self.export_hexo(website)
        else:
            return HttpResponse(status=204)

    def export_markdown(self, website):
        src_dir = os.path.join(website.path, 'source/_posts')
        filename = 'markdown.zip'
        return self.export_zip(src_dir, 'm', filename)

    def export_hexo(self, website):
        src_dir = website.path
        filename = 'hexo.zip'
        return self.export_zip(src_dir, 'h', filename)

    def export_zip(self, src_dir, src_file,  filename):
        dst_dir = self.create_zip(src_dir, filename, src_file=src_file)

        if dst_dir is None:
            return HttpResponse(status=204)

        file = open(dst_dir, 'rb')
        response = FileResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{}"'.format(filename)

        os.remove(dst_dir)
        return response

    @staticmethod
    def create_zip(src_dir, dst_file, src_file='m', dst_dir='/tmp'):
        dst_file = os.path.join(dst_dir, dst_file)
        script = os.path.join(SCRIPT_PATH, 'export.sh')
        command = "bash {} {} {} {}".format(script, src_file, src_dir, dst_file)
        if os.system(command) == 0:
            return dst_file
        else:
            return None
