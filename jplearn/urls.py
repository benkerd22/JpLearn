from django.urls import path

from . import views

urlpatterns = [
    path('test/', views.test, name='test'),
    path('test/next', views.next, name='next'),
    path('test/ttf', views.ttf, name='ttf'),
    path('test/audio/<str:q>/', views.audio, name='audio'),
]