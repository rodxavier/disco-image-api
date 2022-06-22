from django.http import Http404
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin

from rest_framework import viewsets

from .models import ImageUrl, UploadedImage
from .serializers import UploadedImageSerializer


class UploadedImageViewSet(viewsets.ModelViewSet):
    serializer_class = UploadedImageSerializer

    def get_queryset(self):
        user = self.request.user
        return UploadedImage.objects.filter(user=user)


class ImageUrlView(View, SingleObjectMixin):
    model = ImageUrl
    http_method_names = ["get"]

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj.expired:
            raise Http404("Link is expired.")
        return obj
