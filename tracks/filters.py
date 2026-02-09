import django_filters
from .models import Track


class TrackFilter(django_filters.FilterSet):
    genre = django_filters.CharFilter(field_name="genre__slug", lookup_expr="exact")
    mood = django_filters.CharFilter(field_name="mood__slug", lookup_expr="exact")
    min_duration = django_filters.NumberFilter(field_name="duration", lookup_expr="gte")
    max_duration = django_filters.NumberFilter(field_name="duration", lookup_expr="lte")
    min_bpm = django_filters.NumberFilter(field_name="bpm", lookup_expr="gte")
    max_bpm = django_filters.NumberFilter(field_name="bpm", lookup_expr="lte")
    language = django_filters.CharFilter(field_name="language", lookup_expr="iexact")
    artist = django_filters.CharFilter(field_name="artist_name", lookup_expr="icontains")
    featured = django_filters.BooleanFilter(field_name="is_featured")
    created_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")

    class Meta:
        model = Track
        fields = [
            "genre", "mood", "min_duration", "max_duration",
            "min_bpm", "max_bpm", "language", "artist",
            "featured", "created_after",
        ]
