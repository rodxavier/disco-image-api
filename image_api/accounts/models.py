from django.contrib.auth.models import AbstractUser
from django.db import models

from common.mixins import TimestampedModel


class Plan(TimestampedModel):
    name = models.CharField(max_length=40)
    presets = models.ManyToManyField("images.ImagePreset", related_name="plans")
    can_generate_expiring_links = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class User(AbstractUser, TimestampedModel):
    plan = models.ForeignKey(
        "Plan",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="subscribed_users",
    )

    def __str__(self):
        return self.username
