from collections import defaultdict

from django.db import transaction
from rest_framework import serializers

from .models import ImageUrl, UploadedImage


class UploadedImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True)
    expire = serializers.IntegerField(
        max_value=30000,
        min_value=300,
        write_only=True,
        required=False,
    )
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    image_links = serializers.SerializerMethodField()

    class Meta:
        model = UploadedImage
        fields = ["id", "image", "image_links", "expire", "user"]

    @transaction.atomic
    def create(self, validated_data):
        expire = validated_data.pop("expire", None)
        uploaded_image = UploadedImage.objects.create(**validated_data)
        self._create_image_urls(uploaded_image, expire)
        return uploaded_image

    @transaction.atomic
    def update(self, instance, validated_data):
        expire = validated_data.pop("expire", None)
        instance = super().update(instance, validated_data)
        self._create_image_urls(instance, expire)
        return instance

    def _create_image_urls(self, uploaded_image, expire):
        user = self.context["request"].user
        presets = user.plan.presets.all()
        ImageUrl.objects.bulk_create(
            [
                ImageUrl(preset=preset, image=uploaded_image, expire=expire)
                for preset in presets
            ]
        )

    def validate_expire(self, value):
        user = self.context["request"].user
        if not user.plan.can_generate_expiring_links:
            raise serializers.ValidationError(
                "User is not allowed to create expiring links"
            )
        return value

    def get_image_links(self, obj):
        urls = obj.imageurl_set.all()
        image_links = defaultdict(list)
        for url in urls:
            image_links[url.preset.name].append(
                {
                    "url": url.generate_url(self.context["request"]),
                    "expired": url.expired,
                    "expire_at": url.expire_at,
                }
            )
        return image_links


class ExpireOnlySerializer(UploadedImageSerializer):
    image = None

    class Meta:
        model = UploadedImage
        fields = ["id", "image_links", "expire", "user"]
