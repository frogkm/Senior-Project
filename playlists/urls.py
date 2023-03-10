from django.urls import path
from . import views

app_name = 'playlists'

urlpatterns = [
    path('playlist_board/', views.playlist_board, name="playlist_board"),
    path('my_playlists/', views.get_playlist, name='get_playlist'),
    path('my_playlists/search', views.get_playlist_byname, name='get_playlist_byname'),
]
 
