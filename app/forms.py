from django import forms
from .models import CustomUser, Category, Brand, Product, ProductVariation, ProductReview, Appointment, Selling
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model
from datetime import date

# Custom Password Reset Forms
class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form with styled email field"""
    email = forms.EmailField(
        label="Email Address",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email',
            'autofocus': True,
        })
    )

class CustomSetPasswordForm(SetPasswordForm):
    """Custom set password form with styled password fields"""
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password',
            'autocomplete': 'new-password',
            'autofocus': True,
        })
    )
    new_password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password',
        })
    )

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "First Name", "class": "form-control"}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Last Name", "class": "form-control"}))
    email = forms.CharField(widget=forms.EmailInput(attrs={"placeholder": "Email Address", "class": "form-control"}))
    contact = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Mobile Number", "class": "form-control"}), required=True)
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Username", "class": "form-control"}))
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={"placeholder": "Enter password", "class": "form-control"}))
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(attrs={"placeholder": "Confirm password", "class": "form-control"}))

    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name", "email", "contact", "username", "password1", "password2"]
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered. Please use a different email or try logging in.")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if get_user_model().objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose a different username.")
        return username

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['avatar', 'first_name', 'last_name', 'contact', 'address']
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact Number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Address',
                'rows': 3
            }),
        }

class AvatarForm(forms.ModelForm):
    """Form for updating avatar only - prevents clearing other profile fields"""
    class Meta:
        model = CustomUser
        fields = ['avatar']
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }

class ProfileUpdateForm(UserChangeForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    class Meta:
        model = CustomUser
        fields = ['avatar', 'email', 'first_name', 'last_name', 'contact', 'address', 'username', 'password']

class Add(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'model_3d': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.glb,.gltf',
                'help_text': 'Upload a GLB or GLTF 3D model file'
            }),
        }

class AddCategory(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name']

class AddBrand(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['brand']

class AddVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariation
        fields = ['product_variation', 'description', 'price', 'stock', 'image']
        widgets = {
            'product_variation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 256GB / Red'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'multiple': False}),
        }

class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5}),
            "comment": forms.Textarea(attrs={"rows": 3}),
        }

class AppointmentForm(forms.ModelForm):
    TIME_CHOICES = [
        ("10:00", "10:00 AM"),
        ("11:00", "11:00 AM"),
        ("12:00", "12:00 PM"),
        ("13:00", "01:00 PM"),
        ("14:00", "02:00 PM"),
        ("15:00", "03:00 PM"),
        ("16:00", "04:00 PM"),
        ("17:00", "05:00 PM"),
    ]

    time = forms.ChoiceField(
        choices=TIME_CHOICES,
        widget=forms.Select()
    )

    class Meta:
        model = Appointment
        fields = ['first_name', 'last_name', 'contact', 'email', 'date', 'time']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'contact': forms.TextInput(attrs={'placeholder': 'Contact No.'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'min': date.today().isoformat()
                    }),
        }

class SellingForm(forms.ModelForm):
    agree = forms.BooleanField(required=True, label="I agree to the terms and conditions.")

    class Meta:
        model = Selling
        fields = ['product_name', 'category', 'image', 'description', 'price', 'first_name', 'last_name', 'contact', 'address', 'email', 'selling_date', 'selling_time']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'contact': forms.NumberInput(attrs={'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address'}),
            'address': forms.Textarea(attrs={
                'placeholder': 'Address',
                'rows': 4
            }),
            'selling_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'Select Appointment Date', 'min': date.today().isoformat()}),
            'selling_time': forms.TimeInput(attrs={'type': 'time', 'placeholder': 'Select Appointment Time'}),
            'product_name': forms.TextInput(attrs={'placeholder': 'Product Type'}),
            'category': forms.Select(attrs={'placeholder': 'Select Category'}),
            'price': forms.NumberInput(attrs={'placeholder': 'Asking Price'}),
            'description': forms.Textarea(attrs={
                'placeholder': 'Specs & Description',
                'rows': 4
            }),
        }

    def __init__(self, *args, **kwargs):
        super(SellingForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            if field_name != 'agree':
                self.fields[field_name].required = True

    def clean_selling_date(self):
        selling_date = self.cleaned_data.get('selling_date')
        if selling_date and selling_date < date.today():
            raise forms.ValidationError("The selling appointment date cannot be in the past.")
        return selling_date