"""
Forms for MC RCON Manager
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from captcha.fields import CaptchaField


class UserRegistrationForm(UserCreationForm):
    """
    User registration form with email and captcha
    """
    email = forms.EmailField(
        required=True,
        label=_('Email Address'),
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'placeholder': _('your@email.com')
        })
    )
    
    username = forms.CharField(
        label=_('Username'),
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'placeholder': _('Choose a username')
        })
    )
    
    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'placeholder': _('Enter password')
        })
    )
    
    password2 = forms.CharField(
        label=_('Confirm Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
            'placeholder': _('Confirm password')
        })
    )
    
    captcha = CaptchaField(
        label=_('Verification Code'),
        help_text=_('Please solve the math problem'),
        error_messages={
            'invalid': _('Incorrect verification code. Please try again.')
        }
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'captcha']
    
    def clean_email(self):
        """Validate that email is unique"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('This email address is already registered.'))
        return email
    
    def save(self, commit=True):
        """Save user with email"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
