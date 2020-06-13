from django.views.generic.edit import CreateView, View
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q, ObjectDoesNotExist
from django.forms import ModelForm
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django import forms
from .models import User
from PIL import Image
from io import BytesIO
import uuid
import re
import os

UserModel = get_user_model()


class IndexView(View):
    def get(self, request):
        return render(request, template_name='index.html')


class UserCreateForm(ModelForm):
    password = forms.CharField(label="password")
    re_password = forms.CharField(label="re_password")

    class Meta:
        model = User
        fields = ['email', 'nick']

    def clean_re_password(self):
        password = self.cleaned_data['password']
        re_password = self.cleaned_data['re_password']

        if password != re_password:
            raise ValidationError("Password don't match")

        pattern = '^[A-Za-z0-9]{8,20}$'
        if re.match(pattern, re_password) is None:
            raise ValidationError('Invalid password')

        return re_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


# Create your views here.
class UserSignup(CreateView):
    form_class = UserCreateForm
    template_name = 'signup.html'
    success_url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        return render(request, 'signup.html')

    def get_context_data(self, **kwargs):
        if 'form' not in kwargs:
            form = self.get_form()
        else:
            form = kwargs['form']

        context = {
            'tip': True,
            'title': '创建用户失败',
            'error': form.errors,
        }
        return context


class UserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(email=username))
            if user.check_password(password):
                return user
            else:
                return None
        except ObjectDoesNotExist:
            return None


class UserSignIn(View):

    def get(self, request):
        if request.session.session_key:
            return redirect(reverse('website'))
        else:
            return render(request, template_name='login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = auth.authenticate(username=email, password=password)

        if user is not None and user.is_active:
            auth.login(request, user)
            return redirect(reverse('website'))

        title = '登录失败'
        error = "用户不存在或者密码错误"
        context = {
            'tip': True,
            'title': title,
            'error': error,
        }
        return render(request, 'login.html', context)


class UserSignOut(View):
    @method_decorator(login_required(login_url='/account/login/'))
    def get(self, request):
        auth.logout(request)
        del request.session
        return render(request, 'index.html')


class UserDeleteView(View):
    @method_decorator(login_required(login_url='/account/login/'))
    def post(self, request):
        user = request.user
        password = request.POST.get('password')
        user = auth.authenticate(username=user.email, password=password)

        if user is not None:
            auth.logout(request)
            user.delete()
            return JsonResponse({'url': reverse('index')})

        return JsonResponse({'tip': '注销失败，用户不存在或者密码错误'})


def send_email(content):
    send_mail(
        subject=content['subject'],
        message=content['message'],
        from_email=content['from_email'],
        recipient_list=content['recipient_list'],
        fail_silently=content['fail_silently']
    )


class PasswordReset(View):
    reset_password_email = {
        "subject": "Hexo Web 重置密码",
        "message": "您正在请求重置您在Hexo Web中的账号密码，请不要告诉他人验证码。\n验证码一天内有效，",
        "from_email": "gungnir0504@163.com",
        "recipient_list": [],
        "fail_silently": False
    }

    reset_done_email = {
        "subject": "Hexo Web 重置密码成功",
        "message": "您在Hexo Web中的账号密码已重置，如果不是您的操作，请尽快联系我们。 \n联系方式： gungnir0504@163.com",
        "from_email": "gungnir0504@163.com",
        "recipient_list": [],
        "fail_silently": False
    }

    def get(self, request):
        return render(request, 'reset.html')

    def post(self, request):
        if request.is_ajax():
            # send verification code to user's email
            email = request.POST.get('email')
            verify = str(uuid.uuid4())[0:6]
            try:
                user = User._default_manager.get_by_natural_key(email)
            except ObjectDoesNotExist:
                return JsonResponse({"tip": "用户不存在！"})

            if user is None:
                return JsonResponse({"tip": "用户不存在！"})

            user.verify_code = verify
            user.verify_time = timezone.now()
            user.save()

            reset_email_tmp = dict(PasswordReset.reset_password_email)
            reset_email_tmp['message'] = '{}{}{}'.format(reset_email_tmp['message'], '验证码：', verify)
            reset_email_tmp['recipient_list'] = [email]
            send_email(reset_email_tmp)

            return JsonResponse({'tip': '验证码已发送'})

        else:
            # change user's password
            email = request.POST.get('email')
            password = request.POST.get('password')
            re_password = request.POST.get('re_password')
            code = request.POST.get('verify_code')

            error = None
            content = ""
            try:
                user = User._default_manager.get_by_natural_key(email)
                if user is None or user.is_active == False:
                    error = '用户不存在！'
                    raise ValueError

                if self.verify_code(code, user=user):
                    if password != re_password:
                        error = '新密码不一致'
                        raise ValueError

                    pattern = '^[A-Za-z0-9]{8,20}$'
                    if re.match(pattern, re_password) is None:
                        error = '密码格式错误（8-20位字母或者数字）'
                        raise ValueError

                    user.set_password(re_password)
                    user.save()
                    title = '密码已重置'
                    content = '修改密码成功，前往登录页面进行登录！'

                    reset_done_tmp = dict(PasswordReset.reset_done_email)
                    reset_done_tmp['recipient_list'] = [email]
                    send_email(reset_done_tmp)
                else:
                    title = '重置密码失败'
                    error = '验证码错误！'
            except ValueError:
                title = '重置密码失败'

            context = {
                'tip': True,
                'title': title,
            }

            if error:
                context.update({
                    'content': content
                })
            else:
                context.update({
                    'content': content
                })

            return render(request, 'reset.html', context)

    @staticmethod
    def verify_code(code, user):
        if user.verify_code == code:
            today = timezone.now()
            delta = today - user.verify_time
            if delta.days < 1:
                return True
        return False


# view for personal profile
class ProfileView(View):
    form_widget = {
        'input': 0,
        'textarea': 1,
        'password': 2,
    }
    get_method = ['nick', 'password', 'desc']
    post_method = ['avatar', 'nick', 'password', 'desc']

    @method_decorator(login_required(login_url='/account/login/'))
    def get(self, request, **kwargs):
        try:
            option = kwargs['option']
        except KeyError:
            option = ''

        user = request.user
        if option in ProfileView.get_method:
            handler = getattr(self, 'get_' + option)
            context = handler(user)
            return render(request, 'user_update.html', context)
        else:
            context = self.get_index(user)
            return render(request, 'user.html', context)

    @method_decorator(login_required(login_url='/account/signin/'))
    def post(self, request, **kwargs):
        option = kwargs['option']
        user = request.user
        if option in ProfileView.post_method:
            handler = getattr(self, 'post_' + option)
            context = handler(request, user)
            if context is None:
                return redirect(reverse('user'))
            else:
                return render(request, 'user_update.html', context)

    @staticmethod
    def get_index(user):
        if user.avatar.name == '':
            avatar = None
        else:
            avatar = user.avatar

        desc = user.desc[:10]
        context = {
            'avatar': avatar,
            'nick': user.nick,
            'desc': desc,
            'email': user.email,
            'password': '******',
        }
        return context

    @staticmethod
    def get_nick(user):
        context = {
            'title': '更新您的昵称',
            'desc': '',
            'slug': 'nick',
            'items': [
                {'type': ProfileView.form_widget['input'],
                 'label': '昵称',
                 'name': 'nick',
                 'value': user.nick,
                 },
            ]
        }
        return context

    @staticmethod
    def get_desc(user):
        context = {
            'title': '更新您的个人简介',
            'desc': '',
            'slug': 'desc',
            'items': [
                {'type': ProfileView.form_widget['textarea'],
                 'label': '简介',
                 'name': 'desc',
                 'value': user.desc,
                 },
            ]
        }
        return context

    @staticmethod
    def get_password(user):
        context = {
            'title': '更新您的密码',
            'desc': '',
            'slug': 'password',
            'items': [
                {'type': ProfileView.form_widget['password'],
                 'label': '旧密码',
                 'name': 'password',
                 'value': '',
                 },
                {'type': ProfileView.form_widget['password'],
                 'label': '新密码',
                 'name': 'new_password',
                 'value': '',
                 },
                {'type': ProfileView.form_widget['password'],
                 'label': '确认密码',
                 'name': 're_password',
                 'value': '',
                 },
            ]
        }
        return context

    @staticmethod
    def post_avatar(request, user):
        try:
            # remove old avatar file
            if user.avatar:
                if os.path.isfile(user.avatar.path):
                    os.remove(user.avatar.path)

            user.avatar = request.FILES.get('avatar')
            img = Image.open(user.avatar)
            img = circle_img(img, 30)
            filename = 'avatar-' + str(user.id) + '.png'
            io = BytesIO()
            img.save(fp=io, format='PNG')
            user.avatar.save(filename, ContentFile(io.getvalue()))
            user.save()
        except:
            return None
        return None

    @staticmethod
    def post_nick(request, user):
        try:
            user.nick = request.POST.get('nick')
            user.save()
        except:
            context = ProfileView.get_nick(user)
            context.update({
                'tip': True,
                'tip_title': '修改失败',
                'tip_content': '昵称修改失败'
            })
            return context
        return None

    @staticmethod
    def post_desc(request, user):
        try:
            user.desc = request.POST.get('desc')
            user.save()
        except:
            context = ProfileView.get_desc(user)
            context.update({
                'tip': True,
                'tip_title': '修改失败',
                'tip_content': '修改简介失败'
            })
            return context
        return None

    @staticmethod
    def post_password(request, user):
        content = "修改密码失败，"
        try:
            password = request.POST.get('password')
            new_password = request.POST.get('new_password')
            re_password = request.POST.get('re_password')

            if not user.check_password(password):
                content += '原密码错误'
                raise ValueError

            if new_password != re_password:
                content += '新密码不一致'
                raise ValueError

            pattern = '^[A-Za-z0-9]{8,20}$'
            if re.match(pattern, re_password) is None:
                content += '密码格式错误（8-20位字母或者数字）'
                raise ValueError

            user.set_password(re_password)
            user.save()
        except:
            context = ProfileView.get_password(user)
            context.update({
                'tip': True,
                'tip_title': '修改失败',
                'tip_content': content
            })
            return context
        return None


def circle_img(img, r):
    width = height = 2*r
    if img.width != width and img.height != height:
        tmp = img.resize((height, width))
    else:
        tmp = img
    tmp = tmp.convert('RGBA')
    res = Image.new('RGBA', (2*r, 2*r), (255, 255, 255, 0))
    p_tmp = tmp.load()
    p_res = res.load()

    for i in range(height):
        for j in range(width):
            x = abs(i - r)
            y = abs(j - r)
            if (x**2 + y**2) < r**2:
                p_res[i, j] = p_tmp[i, j]
    return res
