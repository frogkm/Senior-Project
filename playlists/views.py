import random
from django.shortcuts import render
from django.db.models import Q
from recommender.models import Account, Playlist, Song
import spotipy, json
from spotipy.oauth2 import SpotifyClientCredentials


#cid = "988994616c4746f7a3ac3e76fabb8363"
cid = "dbc1e517690640be9d828649c55bcfc9"
#secret = "1f58c0981f9842329d3488d8632eb688"
secret = "e05d976c981c4ad1b4e3fa2d1ea16f04"

spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=cid, client_secret=secret))

def search_public_playlists(search_str):
    query = Playlist.objects.filter(Q(playlist_name__icontains = search_str) | Q(creator__user__username__icontains = search_str), public=True)
    query.order_by('songs')
    playlist_list = list(query)
    random.shuffle(playlist_list)
    return playlist_list[:3]

def playlist_board(request):
    if request.method == 'GET':
         search_str = request.GET.get('search_playlists', None)
         if search_str is None:
            playlists = Playlist.objects.filter(public = True)
            playlist_list = list(playlists)
            firstSongsIds = list()

            for playlist in playlist_list:
                firstSong = playlist.songs.order_by('added').first()
                if playlist.songs.count() > 0:
                    firstSongsIds.append(firstSong.track_id)
            
            if len(firstSongsIds) > 0:
                firstSongTracks = json.loads(json.dumps(spotify.tracks(firstSongsIds)))
                firstSongTracks = firstSongTracks["tracks"]
            else:
                firstSongTracks = list()

            filteredLists = [p for p in playlist_list if p.songs.count() > 0]
            
            for i in range(len(firstSongTracks)):
                track = firstSongTracks[i]
                playlist = filteredLists[i]
                playlist.image = track["album"]["images"][1]["url"]
            return render(request, 'playlists/playlist_board.html', { 'playlists': playlist_list })
         else:
            results = list()
            if search_str != "":
                results = search_public_playlists(search_str)        
            else:
                return render(request, "playlists/playlist_board_results.html", { 'results': results, 'empty': True }) 

            firstSongsIds = list()            
        
            for playlist in results:
                firstSong = playlist.songs.order_by('added').first()
                if playlist.songs.count() > 0:
                    firstSongsIds.append(firstSong.track_id)
            
            if len(firstSongsIds) > 0:
                firstSongTracks = json.loads(json.dumps(spotify.tracks(firstSongsIds)))
                firstSongTracks = firstSongTracks["tracks"]
            else:
                firstSongTracks = list()

            filteredLists = [p for p in results if p.songs.count() > 0]
            
            for i in range(len(firstSongTracks)):
                track = firstSongTracks[i]
                playlist = filteredLists[i]
                playlist.image = track["album"]["images"][1]["url"]
                
            return render(request, "playlists/playlist_board_results.html", { 'results': results, 'empty': False }) 
            
def get_playlist(request):
    account = Account.objects.get(user=request.user)

    if(Playlist.objects.filter(playlist_name = "Liked Songs", creator = account).exists()):
        liked = Playlist.objects.filter(playlist_name = "Liked Songs").get(creator=account)
        if(account.liked_songs.count() == 0):
            for song in liked.songs.all():
                liked.songs.remove(song)
        else:
            for song in account.liked_songs.all():
                liked.songs.add(song)
            for rem in account.disliked_songs.all():
                liked.songs.remove(rem)
    else: 
        liked = Playlist(playlist_name = "Liked Songs", public = False, creator = account)
        liked.save()
    
    playlists = Playlist.objects.filter(creator = account)
    lists = list(playlists)
    lists.remove(liked)
    lists.insert(0, liked)
    no_public = True
    for playlist in lists:
        if playlist.public:
            no_public = False
    
    firstSongsIds = list()

    for playlist in lists:
        firstSong = playlist.songs.order_by('added').first()
        if playlist.songs.count() > 0:
            firstSongsIds.append(firstSong.track_id)

    if len(firstSongsIds) > 0:
        firstSongTracks = json.loads(json.dumps(spotify.tracks(firstSongsIds)))
        firstSongTracks = firstSongTracks["tracks"]
    else:
        firstSongTracks = list()

    filteredLists = [p for p in lists if p.songs.count() > 0]
    for i in range(len(firstSongTracks)):
        track = firstSongTracks[i]
        playlist = filteredLists[i]
        playlist.image = track["album"]["images"][1]["url"]

    # noSongPlaylists = [p for p in lists if p.songs.count() == 0]
    # for playlist in noSongPlaylists:
    #     playlist.image = "https://pic.onlinewebfonts.com/svg/img_331373.png"

    return render(request, 'playlists/my_playlists.html', {'lists': lists, 'no_public':no_public})

def get_playlist_byname(request):
    account = Account.objects.get(user=request.user)
    search_str = request.GET.get('playlist_name', None)
    empty = False
    if(search_str.strip() == ""):
        empty = True

    playlists = Playlist.objects.filter(playlist_name__contains=search_str, creator = account)
    lists = list(playlists)

    firstSongsIds = list()

    for playlist in lists:
        firstSong = playlist.songs.order_by('added').first()
        if playlist.songs.count() > 0:
            firstSongsIds.append(firstSong.track_id)
        
            
    if len(firstSongsIds) > 0:
        firstSongTracks = json.loads(json.dumps(spotify.tracks(firstSongsIds)))
        firstSongTracks = firstSongTracks["tracks"]
    else:
        firstSongTracks = list()
        
    filteredLists = [p for p in lists if p.songs.count() > 0]
    for i in range(len(firstSongTracks)):
        track = firstSongTracks[i]
        playlist = filteredLists[i]
        playlist.image = track["album"]["images"][1]["url"]


    return render(request, "playlists/my_playlist_results.html", { 'lists': lists, 'empty': empty})
