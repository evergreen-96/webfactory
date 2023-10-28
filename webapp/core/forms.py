from django import forms
from django.contrib.auth import get_user_model


User = get_user_model()


class ProducedForm(forms.ModelForm):
    class Meta:
        model = ProducedModel
        exclude = ('worker',)


class ProducedEditForm(forms.ModelForm):
    class Meta:
        model = ProducedModel
        fields = '__all__'


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']


    def gen_password(self):
        f_name = self.data.get('first_name').lower()
        l_name = self.data.get('last_name').lower()
        password = l_name + f_name
        return password


class CustomLoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)


class CustomResetPassForm(forms.Form):
    username = forms.CharField(label='username')
    new_password = forms.CharField(label='new password')

