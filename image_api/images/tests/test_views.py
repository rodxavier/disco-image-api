from http import HTTPStatus
from pathlib import Path
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.http.response import FileResponse
from django.test import TestCase
from django.urls import reverse

from images.models import ImagePreset, ImageUrl, UploadedImage
from accounts.models import Plan, User


image_path = Path(__file__).parent / "files" / "sample_image.png"
sample_image = SimpleUploadedFile(
    name="sample_image.png",
    content=open(image_path, "rb").read(),
    content_type="image/png",
)


class TestImageUrlView(TestCase):
    fixtures = ["fixtures/initial_data.json"]

    def setUp(self):
        self.preset = ImagePreset.objects.first()
        self.image = UploadedImage.objects.create(
            image=sample_image, user=User.objects.first()
        )

    def test_non_get_requests_are_not_allowed(self):
        url = reverse("image-url-view", args=[1])
        res = self.client.post(url)
        self.assertEqual(res.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

        res = self.client.put(url)
        self.assertEqual(res.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

        res = self.client.head(url)
        self.assertEqual(res.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

        res = self.client.options(url)
        self.assertEqual(res.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_non_expired_image_url_returns_image(self):
        image_url = ImageUrl.objects.create(preset=self.preset, image=self.image)
        url = reverse("image-url-view", args=[image_url.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertIsInstance(res, FileResponse)

    def test_expired_image_url_returns_404(self):
        image_url = ImageUrl.objects.create(
            preset=self.preset, image=self.image, expire=0
        )
        url = reverse("image-url-view", args=[image_url.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)


class TestUploadedImageViewSet(TestCase):
    fixtures = ["fixtures/initial_data.json"]

    def setUp(self):
        self.basic_user = User.objects.create_user(
            username="basic_user", plan=Plan.objects.get(name="Basic")
        )
        self.enterprise_user = User.objects.create_user(
            username="enterprise_user", plan=Plan.objects.get(name="Enterprise")
        )
        self.client.force_login(self.basic_user)

    def test_user_can_upload_image(self):
        res = self._upload_file()
        self.assertEqual(res.status_code, HTTPStatus.CREATED)
        self.assertIn("image_links", res.json())

    def test_user_can_list_images(self):
        self._upload_file()
        self._upload_file()
        res = self.client.get(reverse("images-list"))
        self.assertEqual(len(res.json()), 2)

    def test_basic_user_cant_provide_expire(self):
        res = self._upload_file(extra_request_kwargs={"expire": 300})
        self.assertEqual(res.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            res.json()["expire"][0], "User is not allowed to create expiring links"
        )

    def test_enterprise_user_can_provide_expire(self):
        self.client.force_login(self.enterprise_user)
        res = self._upload_file(extra_request_kwargs={"expire": 300})
        self.assertEqual(res.status_code, HTTPStatus.CREATED)

    @patch("rest_framework.throttling.UserRateThrottle.get_rate", return_value="1/day")
    def test_user_throttling_works(self, _mock_throttle):
        self._upload_file()
        res = self._upload_file()
        self.assertEqual(res.status_code, HTTPStatus.TOO_MANY_REQUESTS)

    def _upload_file(self, filepath=image_path, extra_request_kwargs={}):
        with open(filepath, "rb") as img:
            res = self.client.post(
                reverse("images-list"), {"image": img, **extra_request_kwargs}
            )
        return res
