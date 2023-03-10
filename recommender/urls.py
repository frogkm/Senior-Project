from django.urls import path
from . import views

app_name = 'recommender'

urlpatterns = [
    path('home/', views.get_home, name='get_home'),
    path('update_recent_songs/<str:track_curr_id>', views.update_recent_songs, name="update_recent_songs"),
]
 
