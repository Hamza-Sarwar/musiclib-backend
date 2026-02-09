from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TrackViewSet, upload_audio

router = DefaultRouter()
router.register(r"tracks", TrackViewSet, basename="track")

urlpatterns = [
    path("tracks/upload-audio/", upload_audio, name="upload-audio"),
    path("", include(router.urls)),
]
