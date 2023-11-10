from django import forms

from .models import StatBugsModel


class BugEditForm(forms.ModelForm):
    class Meta:
        model = StatBugsModel
        fields = ['bug_description', 'is_solved', 'bug_end_time']
