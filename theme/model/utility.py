from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO


def covert_image_format(img_field, filename, file_format):
    assert file_format == "PNG" or file_format == "JPEG"

    img = Image.open(img_field)
    if file_format == "PNG":
        img = img.convert('RGBA')
    else:
        img = img.convert("RGB")

    io = BytesIO()
    img.save(fp=io, format=file_format)
    img_field.save(filename, ContentFile(io.getvalue()), save=False)
