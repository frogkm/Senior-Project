from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Song(models.Model):
    track_id = models.TextField()
    track_name = models.TextField()
    track_artist = models.TextField()
    track_popularity  = models.FloatField()
    track_album_id  = models.TextField()
    track_album_name = models.TextField()
    track_album_release_date = models.IntegerField()
    danceability = models.FloatField()
    energy = models.FloatField()
    key = models.FloatField()
    loudness = models.FloatField()
    mode = models.FloatField()
    speechiness = models.FloatField()
    acousticness = models.FloatField()
    instrumentalness = models.FloatField()
    liveness = models.FloatField()
    valence = models.FloatField()
    tempo = models.FloatField()
    duration_ms  = models.IntegerField()

    def __str__(self) -> str:
        return str(self.track_name)

class Account(models.Model):
    # Associate this custom Account model with the User model
    # Deleting a User will delete the Account as well
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    liked_songs = models.ManyToManyField(Song, related_name='like_accounts')
    disliked_songs = models.ManyToManyField(Song, related_name='dislike_accounts')
    song_showcase = models.ManyToManyField(Song, related_name='showcase_accounts')
    recent_songs = models.ManyToManyField(Song, through='Added')
    profile_picture = models.ImageField(upload_to='images/', null=True)
    

    def __str__(self) -> str:
        return str(self.user.username)

    @receiver(post_save, sender=User)
    def update_profile_signal(sender, instance, created, **kwargs):
        if created:
            Account.objects.create(user=instance)
        instance.account.save()

class Playlist(models.Model):
    playlist_name = models.CharField(max_length=50)
    songs = models.ManyToManyField(Song, through='playlistAdded')
    public = models.BooleanField()
    creator = models.ForeignKey(Account, on_delete = models.CASCADE)

    def __str__(self) -> str:
        return str(self.playlist_name)
    
class playlistAdded(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    time_added = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-time_added',)

class Added(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    time_added = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-time_added',)
