import mimetypes
import uuid
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.db import models
from django.urls import reverse_lazy
from django.utils import timezone

from PIL import Image


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
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploaded_images",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def filename(self):
        return Path(self.image.path).name

    @property
    def filetype(self):
        mimetype, _ = mimetypes.guess_type(self.filename)
        _, filetype = mimetype.split("/")
        return filetype


class ImageUrl(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    preset = models.ForeignKey("ImagePreset", on_delete=models.CASCADE)
    image = models.ForeignKey("UploadedImage", on_delete=models.CASCADE)
    expire = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("preset", "image")]

    def __str__(self):
        return str(self.id)

    @property
    def expired(self):
        if self.expire is None:
            return False
        return timezone.now() > (self.created_at + timedelta(seconds=self.expire))

    def generate_url(self, request=None):
        url = reverse_lazy("image-url-view", args=[self.id])
        if request:
            url = request.build_absolute_uri(url)
        return url

    def apply_preset(self):
        img = Image.open(self.image.image.path)
        width, height = img.size
        new_height = self.preset.height
        new_width = self.preset.width
        if not new_height and not new_width:
            return img

        if new_height:
            new_width = new_height * width / height
        elif new_width:
            new_height = new_width * height / width

        img = img.resize((new_width, new_height), Image.ANTIALIAS)
        return img
