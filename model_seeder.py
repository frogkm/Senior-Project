import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'music.settings')
django.setup()
from recommender.models import Song, Account, Playlist
import random
import string
from django.contrib.auth.models import User, UserManager
import csv

def show_choices():
    choices = {
        0: seed_models,
        1: delete_models
    }

    print('Choose an option:')
    print('0: Seed Account & Playlist Models')
    print('1: Delete Account & Playlist Models')
    
    option = input()
    try:
        option = int(option)
    except:
        print('Option does not exist. Quitting.')
        return
    choices[option]()

def get_random_string(str_size):
    allowed_chars = string.ascii_letters
    return ''.join(random.choice(allowed_chars) for x in range(str_size))

def seed_models():
    seed_accounts()
    seed_playlists()

def seed_account(username, email=None):
    liked_songs = random.choices(list(Song.objects.all()), k=random.randint(5, 10))
    disliked_songs = random.choices(list(Song.objects.all()), k=random.randint(5, 10))
    song_showcase = random.choices(list(Song.objects.all()), k=3)
    recent_songs = random.choices(list(Song.objects.all()), k=random.randint(10, 20))

    if email == None:
        email = username + '@gmail.com'
    
    user = User.objects.create_user(username = username, email = email, password = 'password')

    if username == 'admin':
        user.is_staff = True
        user.is_superuser = True

    user.account.liked_songs.set(liked_songs)
    user.account.disliked_songs.set(disliked_songs)
    user.account.song_showcase.set(song_showcase)
    user.account.recent_songs.set(recent_songs)

    user.save()

def seed_accounts():
    usernames = ['kiefer', 'jake', 'dylan', 'evan', 'nathanael', 'julia', 'kyle', 'stephen', 'admin']
    for username in usernames:
        seed_account(username = username)
  
def seed_playlists():
    for i in range(50):
        seed_playlist()

def seed_playlist():
    if len(Song.objects.all()) == 0:
        print('Seeding playlists failed. No valid songs in database. Please load songs first.')
        return

    playlist_name = 'Playlist-' + get_random_string(4)
    is_public = bool(random.getrandbits(1))
    account = random.choice(list(Account.objects.all()))
    num_songs = random.randint(1, 40)
    songs = random.choices(list(Song.objects.all()), k=num_songs)

    playlist_values = {
        'playlist_name' : playlist_name,
        'public' : is_public,
        'creator' : account
    }

    playlist = Playlist(**playlist_values)
    playlist.save()
    playlist.songs.set(songs)

def delete_models():
    Playlist.objects.all().delete()
    User.objects.all().delete()

show_choices()
