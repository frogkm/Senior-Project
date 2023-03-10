from django.shortcuts import get_object_or_404, render, redirect
from django.views import generic
from django.http import Http404, HttpResponse
from django.urls import reverse_lazy
from account.forms import ChangePasswordForm, RegisterForm, EditProfileForm, ProfilePictureForm
from django.contrib.auth import views as auth_views
from recommender.models import Account, Song, Playlist, Added, User
from django.db.models import Q
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


response = HttpResponse('Session')

cid = "988994616c4746f7a3ac3e76fabb8363"
#cid = "dbc1e517690640be9d828649c55bcfc9"
#cid = "a6dcc167790a4b06b8ce2f10c3dac354"
secret = "1f58c0981f9842329d3488d8632eb688"
#secret = "e05d976c981c4ad1b4e3fa2d1ea16f04"
#secret = "ef0a5e68b1b14278af2623542e1606f9"

class UserRegisterView(generic.CreateView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')


class UserEditView(generic.UpdateView):
    form_class = EditProfileForm
    template_name = 'registration/edit_profile.html'
    success_url = reverse_lazy('account:profile')

    def get_object(self):
        return self.request.user

class PasswordsChangeView(auth_views.PasswordChangeView):
    form_class = ChangePasswordForm
    template_name = 'registration/change-password.html'
    success_url = reverse_lazy('account:password_success')

    def get_object(self):
        return self.request.user

def password_success(request):
    return render(request, 'registration/password_success.html', {})

def get_song_track_id(song):
    return song.track_id

def profile(request):
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=cid, client_secret=secret))
    account = Account.objects.get(user=request.user)
    myProfile = True
    playlists = Playlist.objects.filter(creator = account)
    songs = account.song_showcase.all()
    shuffledSongs = list(songs)
    songShowcase = list(map(get_song_track_id, shuffledSongs))
    returnedShowcase = list()
    likedSongs = len(account.liked_songs.all())
    lists = list(playlists)
    privatePlaylists = 0
    publicPlaylists = 0
    profilePic = account.profile_picture

    if (songShowcase is not None):
        for i in range(len(songShowcase)):
            song_track_id = songShowcase[i]
            track = spotify.track(song_track_id)
            try:
                track["image"] = track["album"]["images"][1]["url"]
                track["artist"] = Song.objects.get(track_id=song_track_id).track_artist
            except:
                print("failed to find image or artist")
            if track["preview_url"] is not None:
                returnedShowcase.append(track)

    for playlist in lists:
        if playlist.public == False:
            privatePlaylists+=1
        else:
            publicPlaylists+=1
    return render(request, 'registration/profile.html', {'privatePlaylists': privatePlaylists, 'publicPlaylists': publicPlaylists, 'likedSongs':likedSongs, 'songs':returnedShowcase, 'myProfile':myProfile, 'profilePic':profilePic})

def friendProfile(request, uname):
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=cid, client_secret=secret))
    friendUser = get_object_or_404(User, username=uname)
    if(friendUser == request.user):
        myProfile = True
    else:
        myProfile = False
    account = Account.objects.get(user = friendUser)
    playlists = Playlist.objects.filter(creator = account)
    songs = account.song_showcase.all()
    shuffledSongs = list(songs)
    songShowcase = list(map(get_song_track_id, shuffledSongs))
    returnedShowcase = list()
    likedSongs = len(account.liked_songs.all())
    lists = list(playlists)
    privatePlaylists = 0
    publicPlaylists = 0
    profilePic = account.profile_picture

    if (songShowcase is not None):
        for i in range(len(songShowcase)):
            song_track_id = songShowcase[i]
            track = spotify.track(song_track_id)
            try:
                track["image"] = track["album"]["images"][1]["url"]
                track["artist"] = Song.objects.get(track_id=song_track_id).track_artist
            except:
                print("failed to find image or artist")
            if track["preview_url"] is not None:
                returnedShowcase.append(track)

    for playlist in lists:
        if playlist.public == False:
            privatePlaylists+=1
        else:
            publicPlaylists+=1
    return render(request, 'registration/profile.html', {'privatePlaylists': privatePlaylists, 'publicPlaylists': publicPlaylists, 'likedSongs':likedSongs, 'songs':returnedShowcase, 'myProfile':myProfile, 'username':uname, 'profilePic':profilePic})

def profilePictureChange(request):
    account = Account.objects.get(user=request.user)
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=account)
        if form.is_valid():
            form.save()
            return redirect('http://localhost:8000/recommender/home')
    else:
        form = ProfilePictureForm(instance=account)
    return render(request, 'registration/profile_picture.html', {'form': form})
 