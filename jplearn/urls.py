from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.welcome),
    path('login/', auth_views.LoginView.as_view(template_name='jplearn/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='jplearn/logout.html'), name='logout'),
    path('test/', views.test, name='test'),
    path('test/next', views.next, name='next'),
    path('test/ttf', views.ttf, name='ttf'),
    path('test/audio/<str:q>/', views.audio, name='audio'),
]