from django import forms
from .models import SignUp


class EmailSignUpForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={
        "type": "email",
        "name" : "email",
        "placeholder" : "your@email.com",
        "id" : "email",
    }), label="")
    class Meta:
        model = SignUp
        fields = ('email',)