import django_filters
from .models import Track


class TrackFilter(django_filters.FilterSet):
    genre = django_filters.CharFilter(field_name="genre__slug", lookup_expr="exact")
    mood = django_filters.CharFilter(field_name="mood__slug", lookup_expr="exact")
    min_duration = django_filters.NumberFilter(field_name="duration", lookup_expr="gte")
    max_duration = django_filters.NumberFilter(field_name="duration", lookup_expr="lte")
    min_bpm = django_filters.NumberFilter(field_name="bpm", lookup_expr="gte")
    max_bpm = django_filters.NumberFilter(field_name="bpm", lookup_expr="lte")
    featured = django_filters.BooleanFilter(field_name="is_featured")

    class Meta:
        model = Track
        fields = ["genre", "mood", "min_duration", "max_duration", "min_bpm", "max_bpm", "featured"]
