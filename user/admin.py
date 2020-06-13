from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms
from .models import User
import re


class UserCreateForm(ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email']

    def clean_password2(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']

        if password1 != password2:
            raise ValidationError("Password don't match")

        pattern = '^[A-Za-z0-9]{8,20}$'
        if re.match(pattern, password2) is None:
            raise ValidationError('Invalid password')

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


# Register your models here.
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreateForm

    list_display = ('email', 'date_joined')
    list_filter = ('is_admin',)
    filter_horizontal = ()
    ordering = ('email',)

    fieldsets = (
        ('Profile', {
            'description': 'personal information of user.',
            'fields': ('email',
                       'nick',
                       'desc',
                       'avatar',
                       'date_joined',)
        }),
        ('Security', {
            'description': 'security information of user',
            'fields': ('password',)
        }),
        ('Directory',{
            'description': 'directory for user',
            'fields': ('user_relative_path', 'photo_relative_path')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


# unregister the Group model from admin.
admin.site.unregister(Group)
