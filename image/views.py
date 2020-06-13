from django.db.models import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.generic import View
from django.core.files.base import ContentFile
from .models import ImageModel
from io import BytesIO
from PIL import Image
import uuid
import os


# Create your views here.
class ImageView(View):
    @method_decorator(login_required(login_url='/account/login/'))
    def get(self, request):
        image_qs = ImageModel.objects.filter(owner=request.user)

        class TempImage:
            def __init__(self):
                self.id = None
                self.name = None
                self.abs_url = None
                self.relative_url = None

        image_list = []
        for image in image_qs:
            t_img = TempImage()
            t_img.id = image.id
            t_img.name = image.img.name.split('/')[-1]
            t_img.abs_url = image.abs_url(request.build_absolute_uri())
            t_img.relative_url = image.img.url
            image_list.append(t_img)

        context = {
            'images': image_list,
        }
        return render(request, 'image.html', context)


class CreateImage(View):

    @method_decorator(login_required(login_url='/account/login/'))
    def post(self, request):
        success = 0
        message = 'error'
        url = ''

        user = request.user
        img_file = request.FILES.get('editormd-image-file')

        if img_file:
            try:
                suffix = img_file.name.split('.')[-1]
                if suffix == 'jpg':
                    suffix = 'jpeg'
                elif suffix == '':
                    suffix = 'png'

                img = Image.open(img_file)
                io = BytesIO()
                img.save(fp=io, format=suffix.upper())

                if not os.path.exists(user.photo_path):
                    os.mkdir(user.photo_path)

                filename = '{}.{}'.format(str(uuid.uuid4())[:8], suffix)

                image = ImageModel.objects.create(img=None, owner=user)
                image.img.save(filename, ContentFile(io.getvalue()))
                image.save()

                success = 1
                url = image.abs_url(request.build_absolute_uri())
            except ValueError as e:
                print(e)
                message = '图片格式不支持'
        else:
            message = '请选择本地图片'

        context = {
            'success': success,
            'message': message,
            'url': url,
        }
        return JsonResponse(context)


class DeleteImage(View):
    def get(self, request, **kwargs):
        try:
            pk = kwargs['pk']
            image = ImageModel.objects.get(pk=pk, owner=request.user)
            image.delete()
            return redirect(to='image')
        except KeyError:
            return HttpResponseBadRequest()
        except ObjectDoesNotExist:
            return HttpResponseBadRequest()
