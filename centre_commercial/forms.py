from django import forms
from .models import Profile, Mall, Shop, Event, ContactMessage, Product, Promotion, Order, OrderItem, ShopReview, ShopSocial, ShopValidation, WorkingHours, ShopHoliday, ArticleBlog
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm



class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter username'
    }))
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter password'
    }))

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image','role', 'phone']
        widgets = {
            'image': forms.FileInput(
                    attrs={
                        'class': 'd-none',
                        'accept': 'image/*',
                        'id': 'imageUpload',
                        'style': 'display:none;'
                    }
                    ),
            'role' : forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }



class NewUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():

            # Add Bootstrap / UI class
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })

        # Optional: better password UX
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })

        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmer le mot de passe'
        })



class MallForm(forms.ModelForm):
    """Formulaire CRUD pour le modèle Mall."""

    class Meta:
        model = Mall
        fields = [
            'manager',
            'name', 'city', 'region', 'address',
            'image', 
            'description', 'description_short',
            'number_of_shops', 'number_of_parking_spaces',
            'opening_time','closing_time',
            'phone', 'email', 'website',
            'is_open', 'is_featured',
            'opening_date', 'badge',
        ]
        widgets = {
            'manager': forms.Select(attrs={'class': 'form-control'}),
            'name':               forms.TextInput(attrs={'placeholder': 'Ex : YESMALL'}),
            'city':             forms.Select(),
            'region':            forms.TextInput(attrs={'placeholder': 'Ex : Nouvelle Ville Ali Mendjeli'}),
            'address':           forms.TextInput(attrs={'placeholder': 'Ex : Route nationale 3, …'}),
            'description':       forms.Textarea(attrs={'rows': 4, 'placeholder': 'Description du centre…'}),
            'description_short':forms.TextInput(attrs={'placeholder': 'Résumé en 180 caractères max'}),

            'number_of_shops':  forms.NumberInput(attrs={'min': 0}),
            'number_of_parking_spaces':  forms.NumberInput(attrs={'min': 0}),

            'opening_time':    forms.TimeInput(attrs={'placeholder': 'Ex : 10h'}),
            'closing_time':   forms.TimeInput(attrs={'placeholder': 'Ex : 22h'}),

            'phone':         forms.TextInput(attrs={'placeholder': '+213 XX XX XX XX'}),
            'email':             forms.EmailInput(attrs={'placeholder': 'contact@yesmall.dz'}),
                      
            'opening_date':  forms.DateInput(attrs={'type': 'date'}),
            'badge':             forms.TextInput(attrs={'placeholder': 'Ex : Nouveau, Phare, Bientôt'}),
        }

class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = [
            'owner',
            'mall',
            'name', 'slug', 'category', 'description', 
            'logo', 'cover', 'phone', 'location', 
            'email', 'website', 'is_featured', 'is_closed',
            'observation'
        ]
        widgets = {
            'owner': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'mall': forms.Select(attrs={'class': 'form-control'}),
            'name':        forms.TextInput(attrs={ 'class': 'form-input', 'required': True, 'placeholder': 'Ex: Global Tech Store',}),
            'slug':        forms.TextInput(attrs={ 'class': 'form-input', 'required': True, 'placeholder': 'Ex: Global Tech Store',}),
            'category':    forms.Select(attrs={'class': 'form-control', 'required': True}),
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
        fields = ['category', 'name','description', 'price', 'old_price', 'image']
        widgets = {
            'category':  forms.Select(attrs={'class': 'form-select'}),
            'name':      forms.TextInput(attrs={'placeholder': 'Ex: Smartphone X Pro', 'class': 'form-input'}),
            'description': forms.Textarea(attrs={'placeholder': 'Describe the product...','rows': 4,'class': 'form-control',}),
            'price':     forms.NumberInput(attrs={'placeholder': '0.00', 'class': 'form-input'}),
            'old_price': forms.NumberInput(attrs={'placeholder': '0.00 (Optional)', 'class': 'form-input'}),
            'image':     forms.ClearableFileInput(attrs={'class': 'form-file'}),
        }

class PromotionForm(forms.ModelForm):
    class Meta:
        model = Promotion
        fields = ['product', 'title', 'description', 'image', 'start_date', 'end_date']
        widgets = {
            'product':     forms.Select(attrs={'class': 'form-select'}),
            'title':       forms.TextInput(attrs={'placeholder': 'Ex: Summer Sale -30%', 'class': 'form-input'}),
            'description': forms.Textarea(attrs={'placeholder': 'Describe the promotion...', 'rows': 3, 'class': 'form-control'}),
            'image':       forms.ClearableFileInput(attrs={'class': 'form-file'}),
            'start_date':  forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'end_date':    forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        }

class ArticleBlogForm(forms.ModelForm):
    class Meta:
        model = ArticleBlog
        fields = ['title', 'content', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Ex: Nouvelles tendances été 2026', 'class': 'form-input'}),
            'content': forms.Textarea(attrs={'placeholder': 'Contenu de l\'article...', 'rows': 8, 'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-file'}),
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'image', 'location', 'date', 'start_event', 'end_event']
        widgets = {
            'title':       forms.TextInput(attrs={'placeholder': 'Ex: Soirée Jazz Live', 'class': 'form-input'}),
            'description': forms.Textarea(attrs={'placeholder': 'Décrivez l\'événement...', 'rows': 4, 'class': 'form-control'}),
            'image':       forms.ClearableFileInput(attrs={'class': 'form-file'}),
            'location':    forms.TextInput(attrs={'placeholder': 'Ex: Place Centrale, Niveau 2', 'class': 'form-input'}),
            'date':        forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-input'}, format='%Y-%m-%dT%H:%M'),
            'start_event': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-input'}, format='%Y-%m-%dT%H:%M'),
            'end_event':   forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-input'}, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['date', 'start_event', 'end_event']:
            self.fields[field_name].input_formats = ['%Y-%m-%dT%H:%M']

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

#----------------------------- Order Form ----------------------------------

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['address', 'payment_method', 'notes']

        widgets = {
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter delivery address'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional notes'
            }),
        }

        labels = {
            'address': 'Delivery Address',
            'payment_method': 'Payment Method',
            'notes': 'Notes',
        }

class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', 'address', 'payment_method', 'notes']

        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter delivery address'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional notes'
            }),
        }

        labels = {
            'status': 'Order Status',
            'address': 'Delivery Address',
            'payment_method': 'Payment Method',
            'notes': 'Notes',
        }

#----------------------------- Order Item Form ----------------------------------
class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    fields=['product', 'quantity', 'price', 'status', 'notes'],
    extra=0,
    can_delete=True
)

#----------------------------- Shop Review Form ----------------------------------
class ShopReviewForm(forms.ModelForm):
    class Meta:
        model = ShopReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} Stars') for i in range(5, 0, -1)], attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write your review here...'}),
        }

#----------------------------- Shop Social Form ----------------------------------
class ShopSocialForm(forms.ModelForm):
    class Meta:
        model = ShopSocial
        fields = ['facebook', 'instagram', 'twitter', 'tiktok', 'whatsapp', 'telegram', 'youtube']
        widgets = {
            'facebook': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://facebook.com/...'}),
            'instagram': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://instagram.com/...'}),
            'twitter': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://twitter.com/...'}),
            'tiktok': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://tiktok.com/@...'}),
            'whatsapp': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://wa.me/...'}),
            'telegram': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://t.me/...'}),
            'youtube': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://youtube.com/...'}),
        }

#----------------------------- Shop Validation Form ----------------------------------
class ShopValidationForm(forms.ModelForm):
    class Meta:
        model = ShopValidation
        fields = ['is_validated', 'observation', 'start_date', 'period']
        widgets = {
            'is_validated': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'period': forms.Select(attrs={'class': 'form-select'}),
        }

#----------------------------- Inline Formsets ----------------------------------
WorkingHoursFormSet = inlineformset_factory(
    Shop, 
    WorkingHours, 
    fields=['day', 'open_time', 'close_time','is_closed'], 
    extra=7, 
    max_num=7,
    can_delete=False,
    widgets={
        'day': forms.HiddenInput(),
        'open_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        'close_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        'is_closed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    }
)

ShopHolidayFormSet = inlineformset_factory(
    Shop,
    ShopHoliday,
    fields=['shop', 'start_date', 'end_date'],
    extra=1,
    widgets={
        'shop': forms.HiddenInput(),
        'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    }
)

