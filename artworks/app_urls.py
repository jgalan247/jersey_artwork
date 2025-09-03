from django.urls import path
from . import views

app_name = 'artworks'

urlpatterns = [
    path('', views.home, name='home'),
    path('gallery/', views.gallery, name='gallery'),
    path('artwork/<int:pk>/', views.artwork_detail, name='artwork_detail'),
    path('upload/', views.artwork_upload, name='upload'),
    path('my-artworks/', views.my_artworks, name='my_artworks'),
]
