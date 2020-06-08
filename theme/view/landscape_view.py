from django.forms import ModelForm
from .base_view import ThemeBaseView
from theme.model.models import LandscapeTheme
from .register import register
import yaml


class LandscapeForm(ModelForm):
    class Meta:
        model = LandscapeTheme
        fields = ['favicon', 'banner', 'excerpt_link', 'position', 'show_count']

    def save(self, commit=True):
        return super(LandscapeForm, self).save(commit)


@register('landscape')
class LandscapeView(ThemeBaseView):

    update_template = 'theme_landscape.html'
    create_template = 'theme_landscape.html'
    model = LandscapeTheme

    def __init__(self):
        super(LandscapeView, self).__init__()

    @staticmethod
    def default_form_context():
        context = {
            'title': 'Landscape',
            'name': 'landscape',
        }
        return context

    def default(self):
        theme = LandscapeView.model()
        return theme

    def _get_create(self):
        context = self.default_form_context()
        form = LandscapeForm()

        position = [t[1] for t in LandscapeView.model.SIDEBAR_ITEMS]
        position_sel = form.fields['position'].initial
        widgets = [(True, t[1], 'widgets' + str(i)) for i, t in enumerate(LandscapeView.model.WIDGETS_ITEMS)]

        context.update({
            'operate': 'create',
            'form': form,
            'position': position,
            'position_sel': position_sel,
            'show_count': True,
            'widgets': widgets,
        })
        return context

    def _get_update(self):
        instance = self.get_instance()
        if instance is None:
            raise ValueError('theme instance is not exist!')

        context = self.default_form_context()
        form = LandscapeForm(instance=instance)

        position = [t[1] for t in LandscapeView.model.SIDEBAR_ITEMS]
        position_sel = instance.position

        widgets_number = len(LandscapeView.model.WIDGETS_ITEMS)
        widgets_no = instance.get_widgets_no()
        widgets_items = [t[1] for t in LandscapeView.model.WIDGETS_ITEMS]
        widgets_name = ['widgets' + str(i) for i in range(widgets_number)]

        widgets_sel = [False] * widgets_number
        for i in range(widgets_number):
            if i in widgets_no:
                widgets_sel[i] = True

        widgets = zip(widgets_sel, widgets_items, widgets_name)

        try:
            favicon = instance.favicon.url
        except ValueError:
            favicon = None

        try:
            banner = instance.banner.url
        except ValueError:
            banner = None

        context.update({
            'id': instance.id,
            'operate': 'update',
            'form': form,
            'position': position,
            'position_sel': position_sel,
            'show_count': instance.show_count,
            'widgets': widgets,
            'favicon': favicon,
            'banner': banner,
        })

        return context

    def update_them(self, request, form):
        theme = form.save(False)
        sel_list = []
        for i in range(len(LandscapeTheme.WIDGETS_ITEMS)):
            name = 'widgets' + str(i)
            w = request.POST.get(name)
            if w and w == 'on':
                sel_list.append(i)
        theme.set_widgets(sel_list)
        return theme

    def _post_create(self, request):
        form = LandscapeForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            return self.update_them(request, form)
        else:
            context = self.default_form_context()
            context.update({
                'form': form,
                'operate': 'create'
            })
            self.errors = context
            return None

    def _post_update(self, request, theme):
        form = LandscapeForm(data=request.POST, files=request.FILES, instance=theme)
        if form.is_valid():
            return self.update_them(request, form)
        else:
            context = self.default_form_context()
            context.update({
                'form': form,
                'operate': 'update',
            })
            self.errors = context
            return None

    def config(self, file, theme):
        try:
            with open(file, 'r') as f:
                y = yaml.safe_load(f)

            y['excerpt_link'] = theme.excerpt_link
            y['sidebar'] = theme.get_position_content()
            y['widgets'] = theme.get_widgets_content()
            y['show_count'] = theme.show_count

            with open(file, 'w') as f:
                yaml.safe_dump(y, f, sort_keys=False, default_flow_style=False,
                               encoding='utf-8', allow_unicode=True)
        except FileNotFoundError:
            return False

        return True

