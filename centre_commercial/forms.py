from django import forms
from .models import ContactMessage, Mall


class MallForm(forms.ModelForm):
    """Formulaire CRUD pour le modèle Mall."""

    class Meta:
        model = Mall
        fields = [
            'name', 'city', 'region', 'address',
            'image', 'bg_color',
            'description', 'short_description',
            'number_of_shops', 
            'opening_time','closing_time',
            'phone', 'email', 'website',
            'is_open', 'is_featured',
            'opening_date', 'badge',
        ]
        widgets = {
            'name':               forms.TextInput(attrs={'placeholder': 'Ex : MALL Constantine'}),
            'city':             forms.Select(),
            'region':            forms.TextInput(attrs={'placeholder': 'Ex : Nouvelle Ville Ali Mendjli'}),
            'address':           forms.TextInput(attrs={'placeholder': 'Ex : Route nationale 3, …'}),
            'bg_color':        forms.TextInput(attrs={'placeholder': 'linear-gradient(135deg,#1a1a2e,#e91e8c)'}),
            'description':       forms.Textarea(attrs={'rows': 4, 'placeholder': 'Description du centre…'}),
            'short_description':forms.TextInput(attrs={'placeholder': 'Résumé en 180 caractères max'}),
            'number_of_shops':  forms.NumberInput(attrs={'min': 0}),

            'opening_time':    forms.TimeInput(attrs={'placeholder': 'Ex : 10h'}),
            'closing_time':   forms.TimeInput(attrs={'placeholder': 'Ex : 22h'}),
            'phone':         forms.TextInput(attrs={'placeholder': '+213 XX XX XX XX'}),
            'email':             forms.EmailInput(attrs={'placeholder': 'contact@yesmall.dz'}),
            'website':          forms.URLInput(attrs={'placeholder': 'https://…'}),
            'opening_date':  forms.DateInput(attrs={'type': 'date'}),
            'badge':             forms.TextInput(attrs={'placeholder': 'Ex : Nouveau, Phare, Bientôt'}),
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
