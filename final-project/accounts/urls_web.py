from django.urls import path
from . import views_web

urlpatterns = [
    path('login/',    views_web.login_view,    name='web-login'),
    path('register/', views_web.register_view, name='web-register'),
    path('logout/',   views_web.logout_view,   name='web-logout'),
    path('me/',       views_web.me_view,       name='web-me'),
    path('me/', views_web.me_view, name='web-me'),
]