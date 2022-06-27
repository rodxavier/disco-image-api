import logging
from io import BytesIO

from django.core.cache import cache
from django.http import FileResponse, Http404
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin

from rest_framework import viewsets

from .models import ImageUrl, UploadedImage
from .serializers import ExpireOnlySerializer, UploadedImageSerializer


class UploadedImageViewSet(viewsets.ModelViewSet):
    serializer_class = UploadedImageSerializer

    def get_queryset(self):
        user = self.request.user
        return UploadedImage.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return ExpireOnlySerializer
        return super().get_serializer_class()


class ImageUrlView(View, SingleObjectMixin):
    model = ImageUrl
    http_method_names = ["get"]

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj.expired:
            raise Http404("Link is expired.")
        return obj

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        cache_key = obj.id
        img_data = cache.get(cache_key)
        if img_data:
            logging.debug("Cache hit")
        else:
            logging.debug("Cache miss")
            img = obj.apply_preset()
            img_data = BytesIO()
            img.save(img_data, obj.image.filetype)
            img_data.seek(0)
            cache.set(cache_key, img_data, obj.expire_in)
        response = FileResponse(
            img_data, filename=f"{obj.preset.name}_{obj.image.filename}"
        )
        return response
