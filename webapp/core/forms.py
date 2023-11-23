from django import forms

from .models import ReportsModel


class ReportEditForm(forms.ModelForm):
    class Meta:
        model = ReportsModel
        fields = ['description', 'is_solved']
