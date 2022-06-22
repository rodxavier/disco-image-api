from django.conf import settings
from django.db import models


class ImagePreset(models.Model):
    name = models.CharField(max_length=40)
    height = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


def user_directory_path(instance, filename):
    return f"{instance.user.id}/{filename}"


class UploadedImage(models.Model):
    image = models.ImageField(upload_to=user_directory_path)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
