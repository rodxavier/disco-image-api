import mimetypes
import uuid
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.db import models
from django.utils import timezone

from rest_framework.reverse import reverse
from PIL import Image

from common.mixins import TimestampedModel


class ImagePreset(TimestampedModel):
    name = models.CharField(max_length=40)
    height = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.name


def user_directory_path(instance, filename):
    return f"{instance.user.id}/{filename}"


class UploadedImage(TimestampedModel):
    image = models.ImageField(upload_to=user_directory_path)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploaded_images",
    )

    @property
    def filename(self):
        return Path(self.image.path).name

    @property
    def filetype(self):
        mimetype, _ = mimetypes.guess_type(self.filename)
        _, filetype = mimetype.split("/")
        return filetype


class ImageUrl(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    preset = models.ForeignKey("ImagePreset", on_delete=models.CASCADE)
    image = models.ForeignKey("UploadedImage", on_delete=models.CASCADE)
    expire = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def expired(self):
        if self.expire is None:
            return False
        return timezone.now() > (self.created_at + timedelta(seconds=self.expire))

    @property
    def expire_in(self):
        if self.expire is None:
            return None
        expire_in = int(
            (self.created_at + timedelta(seconds=self.expire)) - timezone.now()
        )
        return max(0, expire_in)

    def generate_url(self, request=None):
        return reverse("image-url-view", args=[self.id], request=request)

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
