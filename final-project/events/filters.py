import django_filters
from .models import Event


class EventFilter(django_filters.FilterSet):
    start_date__gte = django_filters.DateTimeFilter(field_name='start_date', lookup_expr='gte')
    start_date__lte = django_filters.DateTimeFilter(field_name='start_date', lookup_expr='lte')

    class Meta:
        model = Event
        fields = ['status', 'event_type', 'category']