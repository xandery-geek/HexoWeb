from django.contrib import admin
from .models import Website


# Register your models here.
@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'status', 'creat_time']  # 显示列表的表头
    list_display_links = ['title']  # 显示为链接，可跳转至修改页面
    search_fields = ['title', 'owner__email']  # 查找字段
    list_filter = ('owner', )

    fieldsets = (
        ('Website Basic Information', {
            'description': 'config the basic information for website',
            'fields': ('title', 'subtitle', 'desc', 'keyword', 'author', 'per_page', 'language', 'theme', 'cur_theme')
        }),
        ('Website Information for Deploy', {
            'description': 'config the information for deploy website',
            'fields': ('url', 'repository', 'branch', 'git_username', 'git_email', 'git_password')
        }),
        ('Website owner', {
            'description': 'select the owner for website',
            'fields': ('owner', 'path')
        })
    )
