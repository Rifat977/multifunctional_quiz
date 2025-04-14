from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.utils.translation import gettext_lazy as _

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, error_messages={'required': _('Email field is required.')})
    first_name = forms.CharField(max_length=30, required=True, error_messages={'required': _('First name field is required.')})
    last_name = forms.CharField(max_length=30, required=True, error_messages={'required': _('Last name field is required.')})
    message = forms.CharField(widget=forms.Textarea, required=True, error_messages={'required': _('Message field is required.')})
    gender = forms.ChoiceField(choices=CustomUser.gender_choices, required=True, error_messages={'required': _('Gender field is required.')})

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'gender', 'phone_number']
        error_messages = {
            'username': {
                'required': _('Username field is required.'),
            },
            'password1': {
                'required': _('Password field is required.'),
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].error_messages = {'required': _('Password field is required.')}
        self.fields['password2'].error_messages = {'required': _('Password confirmation field is required.')}
        


    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.gender = self.cleaned_data['gender']
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    identifier = forms.CharField(label="Username or Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

class PasswordResetForm(forms.Form):
    email = forms.EmailField(label='Email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Please enter your email address.")
        return email

class SetPasswordForm(forms.Form):
    new_password1 = forms.CharField(label='New password', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='New password confirmation', widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("The two password fields didn't match.")
        return cleaned_data

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user