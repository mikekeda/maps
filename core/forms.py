from django import forms
from .models import Map


class MapForm(forms.ModelForm):
    class Meta:
        model = Map
        exclude = ('region', 'user', 'slug',)
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 15}),
        }
