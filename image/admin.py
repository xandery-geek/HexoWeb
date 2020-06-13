from django.contrib import admin
from .models import ImageModel


# Register your models here.
@admin.register(ImageModel)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'img', 'owner')
    list_display_links = ('id', )
    ordering = ('id', )

    fieldsets = (
        ('Basic', {
            'description': 'basic information of image.',
            'fields': ('img',
                       'owner',)
        }),
    )
