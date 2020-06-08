from django.contrib import admin
from .model.models import TemplateTheme
from .model.models import LandscapeTheme


# Register your models here.
@admin.register(TemplateTheme)
class ThemeBaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'desc']  # 显示列表的表头
    search_fields = ['name']  # 查找字段

    fieldsets = (
        ('Theme Basic Information', {
            'description': 'config the basic information for theme',
            'fields': ('name', 'desc', 'tags', 'preview', 'preview_url', 'relative_path')
        }),
    )


@admin.register(LandscapeTheme)
class LandscapeThemeAdmin(admin.ModelAdmin):
    list_display = ['template', 'website']  # 显示列表的表头
    search_fields = ['template']  # 查找字段

    fieldsets = (
        ('Theme Basic Information', {
            'description': 'config the basic information for theme',
            'fields': ('template', 'website', 'excerpt_link', 'position', 'widgets', 'show_count')
        }),
        ('Theme Image Fields', {
            'description': 'images for the theme',
            'fields': ('favicon', 'banner',)
        }),
    )