from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Produce
class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)
    class Meta:
        model = User
        fields = ['username','email','password','role']
class ProduceForm(forms.ModelForm):
    class Meta:
        model = Produce
        fields = ['name','quantity_kg','pickup_location']