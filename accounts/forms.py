from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from .models import UserProfile


class SignUpForm(UserCreationForm):
    """
    Extended signup form with email and gender (required)
    """
    email = forms.EmailField(
        required=True,
        help_text='Required. Enter a valid email address.',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    
    gender = forms.ChoiceField(
        choices=[
            ('male', '👨 Male'),
            ('female', '👩 Female'),
            ('other', '🌟 Other'),
            ('prefer_not_to_say', '🔒 Prefer not to say'),
        ],
        required=True,
        help_text='Select your gender for personalized avatar',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'gender', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes to all fields for styling
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Set gender on the user's profile
            if hasattr(user, 'profile'):
                user.profile.gender = self.cleaned_data['gender']
                user.profile.save()
        return user


class UserUpdateForm(forms.ModelForm):
    """
    Form for updating user account information (username, email)
    """
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name (optional)'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name (optional)'}),
        }


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile information (bio, avatar, gender, timezone)
    """
    class Meta:
        model = UserProfile
        fields = ['avatar', 'gender', 'bio', 'timezone']
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell others about yourself, your study goals, interests...'
            }),
            'timezone': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('UTC', 'UTC (Coordinated Universal Time)'),
                ('America/New_York', 'Eastern Time (US)'),
                ('America/Chicago', 'Central Time (US)'),
                ('America/Denver', 'Mountain Time (US)'),
                ('America/Los_Angeles', 'Pacific Time (US)'),
                ('Europe/London', 'London (GMT)'),
                ('Europe/Paris', 'Paris (CET)'),
                ('Asia/Tokyo', 'Tokyo (JST)'),
                ('Asia/Shanghai', 'Shanghai (CST)'),
                ('Asia/Kolkata', 'India (IST)'),
                ('Australia/Sydney', 'Sydney (AEDT)'),
            ]),
        }
        help_texts = {
            'avatar': 'Upload a profile picture (JPG, PNG, max 2MB)',
            'bio': 'Maximum 500 characters',
            'timezone': 'Select your timezone for accurate scheduling',
        }
