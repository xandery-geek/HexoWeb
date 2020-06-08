from django.views.generic import View
from django.shortcuts import render
from django.http import HttpResponseBadRequest
from theme.model.models import TemplateTheme
from .register import THEME_VIEW_CLASS
from .landscape_view import LandscapeView


def get_theme_view(name):
    try:
        return THEME_VIEW_CLASS[name]
    except KeyError:
        return None


def create_default_theme(website, theme):
    theme_view = get_theme_view(theme)
    if theme_view is None:
        return False
    theme = theme_view()
    return theme.default_create(website)


def get_theme_model(name):
    view = get_theme_view(name)
    if view:
        return view.model
    return None


class ThemeView(View):
    def get(self, request):
        theme_list = TemplateTheme.objects.all()

        context = {
            'theme': theme_list,
        }

        return render(request, 'theme.html', context)


class ThemeOperateView(View):

    get_method = ['create', 'update']
    post_method = ['create', 'update', 'delete']

    def __init__(self):
        super().__init__()

    def get_attribute(self):
        pass

    def get(self, request, **kwargs):
        try:
            theme = kwargs['theme']
            option = kwargs['option']
            pk = kwargs['pk']
        except KeyError:
            return HttpResponseBadRequest()

        if option in ThemeOperateView.get_method:
            try:
                theme_view = get_theme_view(name=theme)
                if theme_view is None:
                    raise ValueError('no theme named {}'.format(theme))

                view_instance = theme_view()
                view_instance.pk = pk
                handler = getattr(view_instance, 'get_' + option)
                return handler(request)
            except ValueError as e:
                print(e)
                return HttpResponseBadRequest()

        return HttpResponseBadRequest()

    def post(self, request, **kwargs):
        try:
            theme = kwargs['theme']
            option = kwargs['option']
            pk = kwargs['pk']
        except KeyError:
            return HttpResponseBadRequest()

        if option in ThemeOperateView.post_method:
            try:
                theme_view = get_theme_view(theme)
                if theme_view is None:
                    raise ValueError('no theme named {}'.format(theme))
                view_instance = theme_view()
                view_instance.pk = pk
                handler = getattr(view_instance, 'post_' + option)
                return handler(request)
            except ValueError:
                return HttpResponseBadRequest()

        return HttpResponseBadRequest()
