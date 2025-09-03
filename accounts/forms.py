from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import authenticate
from .models import User, CustomerProfile, ArtistProfile

#from django import forms
#from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
# from .models import User, ArtistProfile

class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form with user type selection."""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    user_type = forms.ChoiceField(choices=User.USER_TYPE_CHOICES, required=True)
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'user_type', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Tailwind CSS classes
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500'
            })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.user_type = self.cleaned_data['user_type']
        if commit:
            user.save()
            # Create corresponding profile
            if user.user_type == 'customer':
                CustomerProfile.objects.create(user=user)
            elif user.user_type == 'artist':
                ArtistProfile.objects.create(user=user, display_name=user.get_full_name())
        return user

class CustomUserChangeForm(UserChangeForm):
    """Custom user change form for admin."""
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'user_type')

class LoginForm(forms.Form):
    """Custom login form."""
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Tailwind CSS classes
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500'
            })
        self.fields['username'].widget.attrs.update({'placeholder': 'Username'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Password'})
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            self.user = authenticate(username=username, password=password)
            if not self.user:
                raise forms.ValidationError('Invalid username or password.')
            if not self.user.is_active:
                raise forms.ValidationError('This account is disabled.')
        return self.cleaned_data

class CustomerProfileForm(forms.ModelForm):
    """Form for updating customer profile."""
    class Meta:
        model = CustomerProfile
        fields = ['date_of_birth', 'address_line_1', 'parish', 'postcode', 'marketing_consent']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Tailwind CSS classes
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    'class': 'w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500'
                })
            else:
                field.widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500'
                })

class ArtistProfileForm(forms.ModelForm):
    """Form for updating artist profile."""
    class Meta:
        model = ArtistProfile
        fields = ['display_name', 'bio', 'website', 'instagram_handle', 'studio_address']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'studio_address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Tailwind CSS classes
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none'
                })
            else:
                field.widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500'
                })

class UserUpdateForm(forms.ModelForm):
    """Form for updating basic user information."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Tailwind CSS classes
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500'
            })

# accounts/forms.py



class CustomerRegistrationForm(UserCreationForm):
    """Registration form for customers (buyers)"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Use email as username
        user.user_type = 'customer'
        user.email_verified = False
        if commit:
            user.save()
        return user


class ArtistRegistrationForm(UserCreationForm):
    """Registration form for artists (sellers)"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )
    business_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Business/Artist name (optional)'
        })
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Tell us about yourself and your art...',
            'rows': 4
        }),
        required=False
    )
    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone number'
        })
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Use email as username
        user.user_type = 'artist'
        user.email_verified = False
        
        if commit:
            user.save()
            # Create artist profile
            # Create basic artist profile (fields will be added later)
            ArtistProfile.objects.create(user=user)
            # TODO: Add business_name, bio, phone_number to model
        return user


class ResendVerificationForm(forms.Form):
    """Form to resend verification email"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise ValidationError("No user found with this email address.")
        
        user = User.objects.get(email=email)
        if user.email_verified:
            raise ValidationError("This email is already verified.")
        
        return email