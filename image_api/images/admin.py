from django.contrib import admin

from .models import ImagePreset, UploadedImage

admin.site.register(ImagePreset)
admin.site.register(UploadedImage)
