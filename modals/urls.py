from django.urls import path
from . import views

app_name = 'modals'

urlpatterns = [
    path('song_search_modal/', views.song_search, name="song_search"),
    path('showcase_search_save/', views.showcase_search_save, name="showcase_search_save"),
    path('showcase_song_delete/', views.showcase_song_delete, name="showcase_song_delete"),
    path('showcase_songs/', views.showcase_songs, name="showcase_songs"),
    path('song_search_results/', views.song_search_results, name="song_search_results"),
    path('song_search_results/<str:song_str>', views.song_search_results, name="song_search_results"),
    path('song_search_save/', views.song_search_save, name="song_search_save"),
    path('playlist_edit_save/', views.playlist_edit_save, name="playlist_edit_save"),
    path('playlist_edit_save/<int:playlist_id>/', views.playlist_edit_save, name="playlist_edit_save"),
    path('playlist_save_copy/<int:playlist_id>/', views.playlist_save_copy, name="playlist_save_copy"),
    path('playlist_detail/<int:playlist_id>/', views.playlist_detail_content, name="playlist"),
    path('playlist_edit/', views.playlist_edit_content, name="playlist_new"),
    path('playlist_edit/<int:playlist_id>/', views.playlist_edit_content, name="playlist_edit"),
    path('song_detail/<str:track_curr_id>', views.song_detail_content, name="song" ),
    path('like_dislike/<str:track_curr_id>/<str:status>', views.like_dislike, name="like_dislike"),
    path('playlist_delete/<int:playlist_id>/', views.playlist_delete, name="playlist_delete"),
    path('likeStatus/<str:track_curr_id>', views.likeStatus, name="likeStatus"),
    path('clear_likes/', views.clear_likes, name="clear_likes"),
    path('playlist_delete_track/<int:playlist_id>/<str:track_id>', views.playlist_delete_track, name="playlist_delete_track"),
]
