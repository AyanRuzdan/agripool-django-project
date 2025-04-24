from django.urls import path
from . import views
urlpatterns = [
    path('register/', views.register, name='register'),
    # path('', views.dashboard, name='dashboard'),
    path('create-produce/', views.create_produce, name='create_produce'),
    path('create-transport/', views.create_transport, name='create_transport'),
    path('transport/delete/<int:transport_id>/',
         views.delete_transport, name='delete_transport'),
    path('produce/delete/<int:id>/', views.delete_produce, name='delete_produce'),
    path('', views.home, name='home')

]
