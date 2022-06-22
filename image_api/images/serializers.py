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
        fields = ["image", "image_links", "expire", "user"]

    @transaction.atomic
    def create(self, validated_data):
        expire = validated_data.pop("expire", None)
        uploaded_image = UploadedImage.objects.create(**validated_data)

        user = self.context["request"].user
        presets = user.plan.presets.all()
        for preset in presets:
            ImageUrl.objects.create(preset=preset, image=uploaded_image, expire=expire)
        return uploaded_image

    def validate_expire(self, value):
        user = self.context["request"].user
        if not user.plan.can_generate_expiring_links:
            raise serializers.ValidationError(
                "User is not allowed to create expiring links"
            )
        return value

    def get_image_links(self, obj):
        urls = obj.imageurl_set.all()
        return {
            url.preset.name: url.generate_url(self.context["request"]) for url in urls
        }
