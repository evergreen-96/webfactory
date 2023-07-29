from django import forms
from .models import ProducedModel


class ProducedForm(forms.ModelForm):
    class Meta:
        model = ProducedModel
        fields = '__all__'
