from django.urls import path
from . import views_web

urlpatterns = [

    path('', views_web.event_list, name='web-event-list'),
    path('<int:pk>/', views_web.event_detail, name='web-event-detail'),
    
  
    path('create/', views_web.create_event, name='create-event'),
    path('<int:pk>/edit/', views_web.edit_event, name='edit-event'),
    path('<int:pk>/delete/', views_web.delete_event, name='delete-event'),
    

    path('<int:pk>/registrations/', views_web.register_event, name='register-event'),
    path('<int:pk>/registrations/<int:reg_id>/cancel/', views_web.cancel_registration, name='cancel-registration'),
    
 
    path('my-registrations/', views_web.my_registrations, name='my-registrations'),
    path('my-events/', views_web.my_events, name='my-events'),
]