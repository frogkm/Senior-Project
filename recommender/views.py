from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from .models import Account, Song, Added
from datetime import datetime, timezone
import random
from django.db.models import Q
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

response = HttpResponse('Session')

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

def get_recent_track_ids(account):
    query = account.recent_songs.all().order_by('added')
    return list(map(get_song_track_id, query))

def get_recommendation_track_ids(account):
    numLikedSongs = len(account.liked_songs.all())

    if numLikedSongs == 0:
        allSongs = list(Song.objects.all())
        random.shuffle(allSongs)
        return [None, list(map(get_song_track_id, allSongs))]

    liked_songs = list(account.liked_songs.all())
    random.shuffle(liked_songs)
    selected_song = liked_songs.pop()

    bottomRange = 0.6
    topRange = 1.4

    # all_attributes = ["danceability", "energy", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo"]
    all_attributes = ["danceability", "energy", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo"]

    random.shuffle(all_attributes)

    all_attributes = all_attributes[:5]

    filter = Q()

    if all_attributes.__contains__("danceability"):
        filter &= Q(danceability__range=(selected_song.danceability * bottomRange, selected_song.danceability * topRange))
    if all_attributes.__contains__("energy"):
        filter &= Q(energy__range=(selected_song.energy * bottomRange, selected_song.energy * topRange))
    if all_attributes.__contains__("speechiness"):
        filter &= Q(speechiness__range=(selected_song.speechiness * bottomRange, selected_song.speechiness * topRange))
    if all_attributes.__contains__("acousticness"):
        filter &= Q(acousticness__range=(selected_song.acousticness * bottomRange, selected_song.acousticness * topRange))
    if all_attributes.__contains__("instrumentalness"):
        filter &= Q(instrumentalness__range=(selected_song.instrumentalness * bottomRange, selected_song.instrumentalness * topRange))
    if all_attributes.__contains__("liveness"):
        filter &= Q(liveness__range=(selected_song.liveness * bottomRange, selected_song.liveness * topRange))
    if all_attributes.__contains__("valence"):
        filter &= Q(valence__range=(selected_song.valence * bottomRange, selected_song.valence * topRange))
    if all_attributes.__contains__("tempo"):
        filter &= Q(tempo__range=(selected_song.tempo * bottomRange, selected_song.tempo * topRange))

    query = Song.objects.filter(filter)

    queryList = list(query)

    finalSongList = list()

    for song in queryList:
        try:
            # Ignore Already Liked Songs
            account.liked_songs.get(track_id=song.track_id)
        except:
            try:
                # Ignore Already Disliked Songs
                account.disliked_songs.get(track_id=song.track_id)
            except:
                try:
                    # Ignore Songs in Listening History
                    account.recent_songs.get(track_id=song.track_id)
                except:
                    finalSongList.append(song)

    if (len(finalSongList) > 0): 
        random.shuffle(finalSongList)
        return [selected_song, list(map(get_song_track_id, finalSongList))]
    else:
        allSongs = list(Song.objects.all())
        random.shuffle(allSongs)
        return [None, list(map(get_song_track_id, allSongs))]    

def get_home(request):
    if request.method == 'GET':
        song = request.GET.get('song', None)
        if song is None:
            if request.user.is_authenticated:
                account = Account.objects.get(user=request.user)

                get_recommendations = get_recommendation_track_ids(account)

                recommender_song = get_recommendations[0]

                recommendation_track_ids = get_recommendations[1]
                if len(recommendation_track_ids) > 0:
                    recommendation_tracks = json.loads(json.dumps(spotify.tracks(recommendation_track_ids[:20])))
                    recommendation_tracks = recommendation_tracks["tracks"]
                else:
                    recommendation_tracks = list()

                recommendation_tracks = [p for p in recommendation_tracks if p["preview_url"] is not None]
                
                for recommendation_track in recommendation_tracks:
                    try:
                        recommendation_track["image"] = recommendation_track["album"]["images"][1]["url"]
                        recommendation_track["artist"] = Song.objects.get(track_id=recommendation_track["id"]).track_artist 
                    except:
                        print("failed to find image or artist")

                recent_track_ids = get_recent_track_ids(account)
                if len(recent_track_ids) > 0:
                    recent_tracks = json.loads(json.dumps(spotify.tracks(recent_track_ids[:20])))
                    recent_tracks = recent_tracks["tracks"]
                else:
                    recent_tracks = list()

                recent_tracks = [p for p in recent_tracks if p["preview_url"] is not None]
                
                for recent_track in recent_tracks:
                    try:
                        recent_track["image"] = recent_track["album"]["images"][1]["url"]
                        recent_track["artist"] = Song.objects.get(track_id=recent_track["id"]).track_artist                        
                    except:
                        print("failed to find image or artist")

                return render(request, "recommender/home.html", {'recent_tracks': recent_tracks, 'recommendation_tracks': recommendation_tracks, 'recommender_song': recommender_song})
            else:
                return render(request, "recommender/home.html")
        else:
            result_tracks = list()
            if song != "":
                query = Song.objects.filter(track_name__contains=song)
                res = list(query)
                resp = list(map(get_song_track_id, res))

                result_track_ids = []
                for i in range(len(resp)):
                    result_track_ids.append(resp[i])
                result_tracks = json.loads(json.dumps(spotify.tracks(result_track_ids[:35])))
                result_tracks = result_tracks["tracks"]

                result_tracks = [p for p in result_tracks if p["preview_url"] is not None]

                for result_track in result_tracks:
                    try:
                        result_track["image"] = result_track["album"]["images"][1]["url"]
                        result_track["artist"] = Song.objects.get(track_id=result_track["id"]).track_artist
                    except:
                        print("failed to find image or artist")

            return render(request, "recommender/results_songs.html", {'songs' : result_tracks})

def update_recent_songs(request, track_curr_id=None):
    #Adds song to recently played list through seperate model called Added
    songObject = get_object_or_404(Song, track_id=track_curr_id)
    accountCurr = Account.objects.get(user=request.user)
    
    if len(accountCurr.recent_songs.filter(track_id = track_curr_id)) == 1:
        Added.objects.filter(account = accountCurr, song = songObject).update(time_added = datetime.now(timezone.utc))
    else:
        accountCurr.recent_songs.add(songObject)

    return HttpResponse()