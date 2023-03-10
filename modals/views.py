import datetime
import random
from recommender.models import Song, Playlist, Account, Added
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from pip._vendor.requests import get
from .forms import EditPlaylistForm
from django.core import serializers
import json
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

cid = "988994616c4746f7a3ac3e76fabb8363"
#cid = "dbc1e517690640be9d828649c55bcfc9"
#cid = "a6dcc167790a4b06b8ce2f10c3dac354"
secret = "1f58c0981f9842329d3488d8632eb688"
#secret = "e05d976c981c4ad1b4e3fa2d1ea16f04"
#secret = "ef0a5e68b1b14278af2623542e1606f9"

# Authentication - without user
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=cid, client_secret=secret))

def get_song_track_id(song):
    return song.track_id

def get_playlist_track_ids(songs):
    return list(map(get_song_track_id, songs))

def search_songs(search_str):
    query = Song.objects.filter(Q(track_artist__icontains = search_str) | Q(track_name__icontains = search_str) | Q(track_album_name__icontains = search_str))
    song_list = list(query.values())

    track_ids = list()
    for song in song_list:
        track_ids.append(song["track_id"])
    
    tracks = json.loads(json.dumps(spotify.tracks(track_ids[:30])))
    tracks = list(tracks["tracks"])

    for track in tracks:
        try:
            track["image"] = track["album"]["images"][1]["url"]
            track["artist"] = Song.objects.get(track_id=track["id"]).track_artist
        except:
            print("failed to find image or artist")

    random.shuffle(tracks)
    return tracks[:4]

def song_search_results(request, song_str = None):
    if song_str is not None and song_str != "":
        tracks = search_songs(song_str)
        return render(request, "modals/song_search_results.html", { "tracks": tracks })
    else:
        return render(request, "modals/song_search_results.html", {})

def song_search(request):
    if request.method == 'GET':
        return render(request, "modals/song_search_content.html", {})

@api_view(['POST'])
def song_search_save(request):
    playlist = get_object_or_404(Playlist, pk=request.data['playlist_id'])
    track_ids = request.data['track_ids'].split(' ')

    for track_id in track_ids:
        playlist.songs.add(Song.objects.get(track_id=track_id))

    return JsonResponse({'success' : True})

def playlist_detail_content(request, playlist_id = None):
     
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    playlist_pk = playlist.pk
    playlist_name = playlist.playlist_name
    creator = playlist.creator
    songs = playlist.songs.all()

    track_ids=[]
    tracks=[]
    serialized_tracks=[]

    if (len(songs) > 0):
        track_ids = get_playlist_track_ids(songs)
        tracks = json.loads(json.dumps(spotify.tracks(track_ids)))
        tracks = tracks["tracks"]

        tracks = [p for p in tracks if p["preview_url"] is not None]
                    
        for track in tracks:
            track["artist"] = Song.objects.get(track_id=track["id"]).track_artist 

        serialized_tracks = json.dumps(tracks)
        
        return render(request, "modals/playlist_detail_content.html", locals())
    return render(request, "modals/playlist_detail_content.html", locals())

def playlist_edit_content(request, playlist_id=None):
    new_playlist = False
    form = None
    if playlist_id is None:
        form = EditPlaylistForm(initial={'playlist_name' : "untitled playlist", 'is_public' : False})
        new_playlist = True
        return render(request, "playlist_edit/playlist_edit_content.html", locals())
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    form = EditPlaylistForm(initial={'playlist_name' : playlist.playlist_name, 'is_public' : playlist.public})
    return render(request, "playlist_edit/playlist_edit_content.html", locals())

@api_view(['POST'])
def playlist_edit_save(request, playlist_id=None):
    playlist_name = request.data['playlist_name']
    account = Account.objects.get(user=request.user) 
    is_public = request.POST.get('is_public', False)

    if is_public == 'on':
        is_public = True

    if playlist_id is None:
        playlist_values = {
            'playlist_name' : playlist_name,
            'public' : is_public,
            'creator' : account
        }
        playlist = Playlist(**playlist_values)
        playlist.save()
    else:
        playlist = get_object_or_404(Playlist, pk=playlist_id)
        
        regex = re.compile("^[A-Za-z0-9_ -]*$")
        if(not(regex.match(playlist_name) == None) and playlist_name.isspace() == False):
            playlist.playlist_name = playlist_name
        
        playlist.public = is_public
        playlist.save()
        
    return JsonResponse({'success' : True})


@api_view(['POST'])
def playlist_save_copy(request, playlist_id=None):
    playlist = get_object_or_404(Playlist, pk=playlist_id)

    playlist_name = playlist.playlist_name
    account = Account.objects.get(user=request.user) 
    is_public = False
    songs = playlist.songs.all()

    playlist_values = {
        'playlist_name' : playlist_name,
        'public' : is_public,
        'creator' : account
    }
    playlist = Playlist(**playlist_values)
    playlist.save()
    playlist.songs.set(songs)
    return JsonResponse({'success' : True})

@api_view(['POST'])
def playlist_delete(request, playlist_id):
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    playlist.delete()

    return JsonResponse({'success' : True})

def playlist_delete_track(request, playlist_id, track_id):
    playlist = get_object_or_404(Playlist, pk=playlist_id)  
    song = get_object_or_404(Song, track_id=track_id)
    playlist.songs.remove(song)

    return JsonResponse({'success' : True})
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    playlist_name = playlist.playlist_name
        
def song_detail_content(request, track_curr_id = None):
    song = get_object_or_404(Song, track_id=track_curr_id)
    link = "https://open.spotify.com/oembed?url=https://open.spotify.com/track/{}".format(track_curr_id)
    details = get(link).json()
    pictureLink = details.get("thumbnail_url")
    length = (datetime.datetime.fromtimestamp(song.duration_ms /1000).strftime('%M:%S')).lstrip("0")
    return render(request, "modals/song_detail_modal.html", {"song":song, "pictureLink":pictureLink, "length":length})

    

def likeStatus(request, track_curr_id = None):
    account = Account.objects.get(user = request.user)
    status = "None"
    queryLike = account.liked_songs.all()
    likedSongs = list(queryLike)
    queryDislike = account.disliked_songs.all()
    dislikedSongs = list(queryDislike)

    song = get_object_or_404(Song, track_id=track_curr_id)

    if song in likedSongs:
        status = "liked"
    elif song in dislikedSongs:
        status = "disliked"
    
    return JsonResponse({'success' : status})

def like_dislike(request, track_curr_id = None, status = None):
    if request.method == 'POST' and track_curr_id != None:
        account = Account.objects.get(user=request.user)
        likeCheck = len(account.liked_songs.filter(track_id=track_curr_id))
        dislikeCheck = len(account.disliked_songs.filter(track_id=track_curr_id))

        song = get_object_or_404(Song, track_id=track_curr_id)

        if status == "like":
            if likeCheck == 0:
                account.liked_songs.add(song)
                if dislikeCheck == 1:
                    account.disliked_songs.remove(song)
                return JsonResponse({'success' : "liked"})
            else:
                account.liked_songs.remove(song)
                return JsonResponse({'success' : "none"})
        elif status == "dislike":
            if dislikeCheck == 0:
                account.disliked_songs.add(song)
                if likeCheck == 1:
                    account.liked_songs.remove(song)
                return JsonResponse({'success' : "disliked"})
            else:
                account.disliked_songs.remove(song)
                return JsonResponse({'success' : "none"})

@api_view(['POST'])
def showcase_search_save(request):
    account = Account.objects.get(user = request.user)
    track_ids = request.data['track_ids'].split(' ')

    for track_id in track_ids:
        account.song_showcase.add(Song.objects.get(track_id=track_id))

    return JsonResponse({'success' : True})

@api_view(['POST'])
def showcase_song_delete(request):
    account = Account.objects.get(user = request.user)
    track_ids = request.data['track_ids'].split(' ')

    for track_id in track_ids:
        account.song_showcase.remove(Song.objects.get(track_id=track_id))

    return JsonResponse({'success' : True})

def showcase_songs(request):
    account = Account.objects.get(user = request.user)
    query = account.song_showcase.all()
    res = list(query)
    songShowcase = list(map(get_song_track_id, res))
    showcase = []
    if (songShowcase is not None):
        for i in range(len(songShowcase)):
            song_track_id = songShowcase[i]
            track = spotify.track(song_track_id)
            try:
                track["image"] = track["album"]["images"][1]["url"]
                track["artist"] = Song.objects.get(track_id=song_track_id).track_artist
            except:
                print("failed to find image or artist")
            showcase.append(track)

    return render(request, "modals/song_showcase_remove.html", {"songs" : showcase})

@api_view(['POST'])
def clear_likes(request):
    account = Account.objects.get(user = request.user)
    for song in account.liked_songs.all():
        account.liked_songs.remove(song)
    for song in account.disliked_songs.all():
        account.disliked_songs.remove(song)

    account.save()

    return JsonResponse({'success' : True})