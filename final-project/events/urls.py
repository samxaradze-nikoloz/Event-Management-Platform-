from rest_framework_nested import routers
from django.urls import path, include
from .views import EventViewSet, RegistrationViewSet, ReviewViewSet, CategoryViewSet, TagViewSet
from django.urls import path
from . import views

router = routers.DefaultRouter()
router.register(r'events', EventViewSet, basename='events')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'tags', TagViewSet, basename='tags')

events_router = routers.NestedDefaultRouter(router, r'events', lookup='event')
events_router.register(r'registrations', RegistrationViewSet, basename='event-registrations')
events_router.register(r'reviews', ReviewViewSet, basename='event-reviews')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(events_router.urls)),
    path('create/', views.create_event, name='create-event'),
]