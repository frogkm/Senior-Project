from django import forms


class EditPlaylistForm(forms.Form):
    playlist_name = forms.CharField()
    is_public = forms.BooleanField(required=False)


