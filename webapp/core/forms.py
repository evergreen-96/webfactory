from django import forms

from .models import ReportsModel


class BugEditForm(forms.ModelForm):
    class Meta:
        model = ReportsModel
        fields = ['description', 'is_solved', 'end_time']
