from django.forms import ModelForm
from .models import Website


class WebsiteForm(ModelForm):
    class Meta:
        model = Website
        fields = ['title', 'subtitle', 'author', 'per_page', 'url', 'desc', 'keyword',
                  'repository', 'branch', 'git_username', 'git_email', 'git_password']

    def save(self, commit=True):
        website = super().save(commit)
        return website

    def is_valid(self):
        is_valid = super().is_valid()
        if not is_valid:
            return False

        return True
