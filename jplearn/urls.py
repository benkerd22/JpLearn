from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'jplearn'
urlpatterns = [
    path('', views.welcome, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='jplearn/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='jplearn/logout.html'), name='logout'),
    path('test/', views.test, name='test'),
    path('start/', views.start, name='start'),
    path('cdn/ttf', views.ttf, name='ttf'),
    path('cdn/audio', views.audio, name='audio'),
    path('cdn/audio/<str:q>/', views.audio),
    path('dict/', views.dict, name='dict'),
    path('dict/data', views.dictData, name='dictData'),
    path('dict/action', views.dictAction, name='dictAction'),
]