from django.urls import path
from .views import PasswordsChangeView, UserEditView, UserRegisterView
from . import views

app_name = 'account'

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('edit_profile/', UserEditView.as_view(), name='edit_profile'),
    path('password/', PasswordsChangeView.as_view(), name='password'),
    path('password_success/', views.password_success, name='password_success'),
    path('profile/', views.profile, name='profile'),
    path('profile/<str:uname>', views.friendProfile, name='friendProfile'),
    path('profile_picture/', views.profilePictureChange, name='profile_picture'),
]