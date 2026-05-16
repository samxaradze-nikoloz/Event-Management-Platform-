from django.core.cache import cache
from django.db.models import Count, Avg
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response

from .filters import EventFilter
from .models import Category, Tag, Event, Registration, Review, EventMedia
from .permissions import IsOrganizer, IsOwnerOrReadOnly, IsConfirmedAttendee
from .serializers import (
    CategorySerializer, TagSerializer, EventSerializer,
    RegistrationSerializer, ReviewSerializer, EventMediaSerializer
)
from .throttles import RegistrationBurstThrottle

EVENTS_CACHE_KEY = 'events_list'
STATS_CACHE_KEY = 'events_stats'
CACHE_TTL = 60 * 5             


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    filterset_class = EventFilter
    search_fields = ['title', 'description']
    ordering_fields = ['start_date', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Event.objects.select_related('organizer', 'category').prefetch_related('tags')

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsOrganizer()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return [IsAuthenticatedOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)
        cache.delete(EVENTS_CACHE_KEY)
        cache.delete(STATS_CACHE_KEY)

    def perform_update(self, serializer):
        serializer.save()
        cache.delete(EVENTS_CACHE_KEY)
        cache.delete(STATS_CACHE_KEY)

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete(EVENTS_CACHE_KEY)
        cache.delete(STATS_CACHE_KEY)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        cached = cache.get(STATS_CACHE_KEY)
        if cached:
            return Response(cached)

        total_events = Event.objects.count()
        published_events = Event.objects.filter(status='published').count()
        total_registrations = Registration.objects.count()

        events_by_status = {
            item['status']: item['count']
            for item in Event.objects.values('status').annotate(count=Count('id'))
        }

        top_events = list(
            Event.objects.annotate(
                registration_count=Count('registrations'),
                avg_rating=Avg('reviews__rating')
            ).order_by('-registration_count')[:5].values(
                'id', 'title', 'registration_count', 'avg_rating'
            )
        )

        data = {
            'total_events': total_events,
            'published_events': published_events,
            'total_registrations': total_registrations,
            'events_by_status': events_by_status,
            'top_events': top_events,
        }
        cache.set(STATS_CACHE_KEY, data, timeout=CACHE_TTL)
        return Response(data)

    @action(detail=True, methods=['post'], url_path='media',
            parser_classes=[MultiPartParser, FormParser],
            permission_classes=[IsAuthenticated, IsOwnerOrReadOnly])
    def upload_media(self, request, pk=None):
        event = self.get_object()
        serializer = EventMediaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(event=event)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = RegistrationSerializer
    throttle_classes = [RegistrationBurstThrottle]

    def get_queryset(self):
        return Registration.objects.filter(event_id=self.kwargs['event_pk'])

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ('update', 'partial_update'):
            return [IsAuthenticated(), IsOrganizer()]
        if self.action == 'destroy':
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['event'] = Event.objects.get(pk=self.kwargs['event_pk'])
        return context

    def perform_create(self, serializer):
        from notifications.tasks import send_registration_confirmation
        registration = serializer.save()
        send_registration_confirmation.delay(registration.id)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(event_id=self.kwargs['event_pk'])

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsConfirmedAttendee()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsAuthenticated()]
        return [IsAuthenticatedOrReadOnly()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['event'] = Event.objects.get(pk=self.kwargs['event_pk'])
        return context
