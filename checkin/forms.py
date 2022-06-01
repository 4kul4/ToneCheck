from .models import Publics
from django.forms import ModelForm, TextInput

class PublicsForm(ModelForm):
    class Meta:
        model = Publics
        fields = ['public_start',
                  'public_end',
                  'language',
                  'page']