from django.contrib.auth.models import AbstractUser
from django.db import models


class Plan(models.Model):
    name = models.CharField(max_length=40)
    presets = models.ManyToManyField("images.ImagePreset", related_name="plans")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    plan = models.ForeignKey(
        "Plan",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="subscribed_users",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username
