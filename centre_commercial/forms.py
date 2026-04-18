from django import forms
from .models import Profile, Mall, Shop, ContactMessage, Product 
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'phone', 'address']



class MallForm(forms.ModelForm):
    """Formulaire CRUD pour le modèle Mall."""

    class Meta:
        model = Mall
        fields = [
            'name', 'city', 'region', 'address',
            'image', 'bg_color',
            'description', 'description_short',
            'number_of_shops', 'number_of_parking_spaces',
            'opening_time','closing_time',
            'phone', 'email', 'website',
            'is_open', 'is_featured',
            'opening_date', 'badge',
        ]
        widgets = {
            'name':               forms.TextInput(attrs={'placeholder': 'Ex : YESMALL'}),
            'city':             forms.Select(),
            'region':            forms.TextInput(attrs={'placeholder': 'Ex : Nouvelle Ville Ali Mendjeli'}),
            'address':           forms.TextInput(attrs={'placeholder': 'Ex : Route nationale 3, …'}),
            'bg_color':        forms.TextInput(attrs={'placeholder': 'linear-gradient(135deg,#1a1a2e,#e91e8c)'}),
            'description':       forms.Textarea(attrs={'rows': 4, 'placeholder': 'Description du centre…'}),
            'description_short':forms.TextInput(attrs={'placeholder': 'Résumé en 180 caractères max'}),

            'number_of_shops':  forms.NumberInput(attrs={'min': 0}),
            'number_of_parking_spaces':  forms.NumberInput(attrs={'min': 0}),

            'opening_time':    forms.TimeInput(attrs={'placeholder': 'Ex : 10h'}),
            'closing_time':   forms.TimeInput(attrs={'placeholder': 'Ex : 22h'}),

            'phone':         forms.TextInput(attrs={'placeholder': '+213 XX XX XX XX'}),
            'email':             forms.EmailInput(attrs={'placeholder': 'contact@yesmall.dz'}),
            'website':          forms.URLInput(attrs={'placeholder': 'https://…'}),
            
            'opening_date':  forms.DateInput(attrs={'type': 'date'}),
            'badge':             forms.TextInput(attrs={'placeholder': 'Ex : Nouveau, Phare, Bientôt'}),
        }

class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = [
            'name','category', 'description', 
            'logo', 'cover', 'phone', 'location', 
            'email', 'website', 'is_featured', 'is_closed',
            'observation'
        ]
        widgets = {
            'name':        forms.TextInput(attrs={'placeholder': 'Ex: Global Tech Store', 'class': 'form-input'}),
            'category':    forms.Select(),
            'description': forms.Textarea(attrs={'placeholder': 'Describe the shop...', 'rows': 4}),
            'phone':       forms.TextInput(attrs={'placeholder': '+213 XX XX XX XX'}),
            'email':       forms.EmailInput(attrs={'placeholder': 'shop@mall.dz'}),
            'website':     forms.URLInput(attrs={'placeholder': 'https://...'}), 
            'location':    forms.TextInput(attrs={'placeholder': 'Ex: Level 1, North Wing'}),
            'logo':        forms.ClearableFileInput(),
            'cover':       forms.ClearableFileInput(),
            'is_featured': forms.CheckboxInput(),            
            'is_closed':   forms.CheckboxInput(),
            'observation': forms.Textarea(attrs={'placeholder': 'Internal notes...', 'rows': 3}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'price', 'old_price', 'image']
        widgets = {
            'category':  forms.Select(attrs={'class': 'form-select'}),
            'name':      forms.TextInput(attrs={'placeholder': 'Ex: Smartphone X Pro', 'class': 'form-input'}),
            'price':     forms.NumberInput(attrs={'placeholder': '0.00', 'class': 'form-input'}),
            'old_price': forms.NumberInput(attrs={'placeholder': '0.00 (Optional)', 'class': 'form-input'}),
            'image':     forms.ClearableFileInput(attrs={'class': 'form-file'}),
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name':     forms.TextInput(attrs={'placeholder': 'Your name'}),
            'email':   forms.EmailInput(attrs={'placeholder': 'Your email'}),
            'subject':   forms.TextInput(attrs={'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'placeholder': 'Your message', 'rows': 5}),
        }
