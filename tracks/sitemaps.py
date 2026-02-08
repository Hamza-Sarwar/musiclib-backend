from django.contrib.sitemaps import Sitemap
from .models import Track


class TrackSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Track.objects.filter(is_active=True).order_by("-created_at")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f"/tracks/{obj.id}"
