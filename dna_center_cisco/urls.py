from django.urls import path
from . import views

app_name = 'dna_center_cisco'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('auth/', views.authenticate_view, name='auth'),
    path('devices/', views.devices_view, name='devices'),
    path('interfaces/', views.interfaces_view, name='interfaces'),
]
