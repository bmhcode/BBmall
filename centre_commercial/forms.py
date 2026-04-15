from django import forms
from .models import ContactMessage, Mall


class MallForm(forms.ModelForm):
    """Formulaire CRUD pour le modèle Mall."""

    class Meta:
        model = Mall
        fields = [
            'nom', 'ville', 'region', 'adresse',
            'image', 'couleur_bg',
            'description', 'description_courte',
            'nombre_boutiques', 
            'heure_ouverture','heure_fermeture',
            'telephone', 'email', 'site_web',
            'est_ouvert', 'est_en_vedette',
            'ouverture_prevue', 'badge',
        ]
        widgets = {
            'nom':               forms.TextInput(attrs={'placeholder': 'Ex : MALL Constantine'}),
            'ville':             forms.Select(),
            'region':            forms.TextInput(attrs={'placeholder': 'Ex : Nouvelle Ville Ali Mendjli'}),
            'adresse':           forms.TextInput(attrs={'placeholder': 'Ex : Route nationale 3, …'}),
            'couleur_bg':        forms.TextInput(attrs={'placeholder': 'linear-gradient(135deg,#1a1a2e,#e91e8c)'}),
            'description':       forms.Textarea(attrs={'rows': 4, 'placeholder': 'Description du centre…'}),
            'description_courte':forms.TextInput(attrs={'placeholder': 'Résumé en 180 caractères max'}),
            'nombre_boutiques':  forms.NumberInput(attrs={'min': 0}),

            'heure_ouverture':    forms.TimeInput(attrs={'placeholder': 'Ex : 10h'}),
            'heure_fermeture':   forms.TimeInput(attrs={'placeholder': 'Ex : 22h'}),
            'telephone':         forms.TextInput(attrs={'placeholder': '+213 XX XX XX XX'}),
            'email':             forms.EmailInput(attrs={'placeholder': 'contact@yesmall.dz'}),
            'site_web':          forms.URLInput(attrs={'placeholder': 'https://…'}),
            'ouverture_prevue':  forms.DateInput(attrs={'type': 'date'}),
            'badge':             forms.TextInput(attrs={'placeholder': 'Ex : Nouveau, Phare, Bientôt'}),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['nom', 'email', 'sujet', 'message']
        widgets = {
            'nom':     forms.TextInput(attrs={'placeholder': 'Votre nom'}),
            'email':   forms.EmailInput(attrs={'placeholder': 'Votre email'}),
            'sujet':   forms.TextInput(attrs={'placeholder': 'Sujet'}),
            'message': forms.Textarea(attrs={'placeholder': 'Votre message', 'rows': 5}),
        }
