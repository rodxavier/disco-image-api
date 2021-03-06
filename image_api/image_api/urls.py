from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from images.views import ImageUrlView, UploadedImageViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"images", UploadedImageViewSet, basename="images")

urlpatterns = [
    path("image/<pk>/", ImageUrlView.as_view(), name="image-url-view"),
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
