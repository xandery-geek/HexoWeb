from abc import abstractmethod
from django.db.models import ObjectDoesNotExist
from django.views.generic import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from website.models import Website
import os


class ThemeBaseView(View):
    create_template = ''
    update_template = ''
    model = None

    def __init__(self):
        super().__init__()
        self.pk = None
        self.errors = None

    def get_instance(self):
        try:
            return self.__class__.model.objects.get(pk=self.pk)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def create_theme_dir(theme):
        command = "cp -r {} {}".format(theme.template.get_theme_abspath(), theme.get_theme_abspath())
        return os.system(command)

    @staticmethod
    def delete_theme_dir(theme):
        command = "rm -r {}".format(theme.get_theme_abspath())
        return os.system(command)

    def config_theme(self, theme):
        config_filename = os.path.join(theme.get_theme_abspath(), '_config.yml')
        return self.config(config_filename, theme)

    def delete(self, theme):
        return self.delete_theme_dir(theme)

    @abstractmethod
    def _post_create(self, request):
        pass

    @abstractmethod
    def _post_update(self, request, theme):
        pass

    @abstractmethod
    def _get_create(self, ):
        pass

    @abstractmethod
    def _get_update(self):
        pass

    @abstractmethod
    def config(self, file, theme):
        pass

    @abstractmethod
    def default(self):
        pass

    def get_create(self, request):
        context = self._get_create()
        template = self.__class__.create_template
        if template == '':
            raise ValueError('creat template is not assign')
        return render(request, template, context)

    def get_update(self, request):
        context = self._get_update()
        template = self.__class__.update_template
        if template == '':
            raise ValueError('update template is not assign')
        return render(request, template, context)

    def post_update(self, request):
        theme = self.get_instance()
        if theme:
            self._post_update(request, theme)
            theme.save()
            self.config_theme(theme)

            return redirect('website_detail', theme.website.id)
        else:
            template = self.__class__.update_template
            if template == '':
                raise ValueError('update template is not assign')
            return render(request, template, self.errors)

    def post_delete(self, request):
        theme = self.get_instance()
        website = theme.website
        if theme.template.name == website.cur_theme:
            return JsonResponse({'tip': '当前主题正在使用，不能删除'})

        self.delete(theme)
        theme.delete()
        website.delete_theme(theme.template.name)
        success_url = reverse('website_detail', args=(website.id,))
        return JsonResponse({'tip': '主题已经删除', 'url': success_url})

    def post_create(self, request):
        theme = self._post_create(request)
        if theme:
            user = request.user
            website = Website.get_current_website(user.id)
            if website is None:
                raise ValueError('current user does not have a website!')

            theme.website = website
            if not website.add_theme(theme.template.name):
                raise ValueError('user can own only one theme for each template theme!')

            # save theme, create and config theme for website
            theme.save()
            website.save()
            self.create_theme_dir(theme)
            self.config_theme(theme)

            return redirect('website_detail', website.id)
        else:
            template = self.__class__.create_template
            if template == '':
                raise ValueError('creat template is not assign')
            return render(request, template, self.errors)

    def default_create(self, website):
        theme = self.default()
        if theme:
            if website is None:
                raise ValueError('must provide a website!')
            theme.website = website
            # save theme, create and config theme for website
            theme.save()
            self.create_theme_dir(theme)
            self.config_theme(theme)
            return True
        return False
