from django.urls import path
from django.contrib.auth.views import LoginView
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('create-produce/', views.create_produce, name='create_produce'),
    path('create-transport/', views.create_transport, name='create_transport'),
    path('transport/delete/<int:transport_id>/',
         views.delete_transport, name='delete_transport'),
    path('produce/delete/<int:id>/', views.delete_produce, name='delete_produce'),
    path('dashboard/', views.dashboard, name='dashboard')
]
