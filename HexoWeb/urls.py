"""hexo_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings
from user.views import *
from blog.views import *
from website.views import *
from theme.view.views import ThemeView, ThemeOperateView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('account/login/', UserSignIn.as_view(), name='login'),
    path('account/signup/', UserSignup.as_view(), name='signup'),
    path('account/logout/', UserSignOut.as_view(), name='logout'),
    path('account/reset/', PasswordReset.as_view(), name='reset'),
    path('user/information/', ProfileView.as_view(), name='user'),
    path('website/', WebsiteView.as_view(), name='website'),
    path('website/new/', CreateWebsiteView.as_view(), name='website_new'),
    path('website/delete/', DeleteWebsiteView.as_view(), name='website_delete'),
    path('blog/', PostView.as_view(), name='blog'),
    path('edit/', PostOperateView.as_view(), name='editor'),
    re_path(r'^user/update/(?P<option>[\w]+)/$', ProfileView.as_view(), name='user_update'),
    re_path(r'^website/(?P<pk>\d+)/$', WebsiteDetailView.as_view(), name='website_detail'),
    re_path(r'^website/(?P<pk>\d+)/update/(?P<option>[\w]+)$', UpdateWebsiteView.as_view(), name='website_update'),
    re_path(r'^website/themes/$', ThemeView.as_view(), name='website_theme'),
    re_path(r'^website/themes/(?P<pk>\d+)/(?P<theme>[\w]+)/(?P<option>[\w]+)/$', ThemeOperateView.as_view(),
            name='theme_operate'),
    re_path(r'^website/(?P<pk>\d+)/export/(?P<option>[\w]+)$', ExportWebsiteView.as_view(), name='website_export'),
    re_path(r'^blog/(?P<option>[\w]+)/(?P<keyword>[\u4E00-\u9FA5A-Za-z0-9]*)$', PostView.as_view(),
            name='post_detail'),
    re_path(r'^blog/id/(?P<pk>[\d]+)/$', PostDetailView.as_view(), name='post_detail'),
    re_path(r'^edit/(?P<pk>[\d]+)/(?P<option>[\w]+)/$', PostOperateView.as_view(), name='edit_operate'),
    re_path(r'^blog/id/(?P<pk>[\d]+)/(?P<option>[\w]+)/$', PostOperateView.as_view(), name='post_operate'),
    re_path(r'^blog/category/(?P<pk>[\d]+)/$', CategoryView.as_view(), name='category'),
    re_path(r'^blog/category/(?P<pk>[\d]+)/(?P<option>[\w]+)/$', CategoryView.as_view(), name='category_operate'),
    re_path(r'^blog/tag/(?P<pk>[\d]+)/$', TagView.as_view(), name='tag'),
    re_path(r'^blog/tag/(?P<pk>[\d]+)/(?P<option>[\w]+)/$', TagView.as_view(), name='tag_operate'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
