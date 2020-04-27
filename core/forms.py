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
        fields = ('title', 'description', 'unit', 'date_of_information', 'categories', 'grades',
                  'logarithmic_scale', 'end_color', 'start_color', 'opacity')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 15}),
        }
