from .base_view import ThemeBaseView


THEME_VIEW_CLASS = {}


def register(name):
    def decorate(cls):
        if not issubclass(cls, ThemeBaseView):
            raise ValueError('theme view class must subclass ThemeBaseView.')
        THEME_VIEW_CLASS.update({name: cls})
        return cls

    return decorate

