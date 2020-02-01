from django import forms
from django.utils.translation import ugettext_lazy as _

from core.models import Map


class MapForm(forms.ModelForm):
    """ Add map form. """
    # For now 2 is max level of desalination.
    level = forms.IntegerField(label=_('Level of detail'), max_value=2,
                               min_value=1, initial=1)

    class Meta:
        model = Map
        exclude = ('region', 'user', 'slug',)
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 15}),
        }
