from django.urls import path
from . import views_web

urlpatterns = [
    path('', views_web.event_list, name='web-event-list'),
    path('create/', views_web.create_event, name='create-event'),
    path('<int:pk>/', views_web.event_detail, name='web-event-detail'),
]