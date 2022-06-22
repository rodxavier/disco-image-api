from rest_framework import viewsets

from .models import UploadedImage
from .serializers import UploadedImageSerializer


class UploadedImageViewSet(viewsets.ModelViewSet):
    serializer_class = UploadedImageSerializer

    def get_queryset(self):
        user = self.request.user
        return UploadedImage.objects.filter(user=user)
