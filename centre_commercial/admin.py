from django.contrib import admin
from .models import Mall, Magasin, Evenement, Promotion, ContactMessage, ArticleBlog


@admin.register(Mall)
class MallAdmin(admin.ModelAdmin):
    list_display  = ('nom', 'ville', 'region', 'nombre_boutiques','nombre_places_parking', 'est_ouvert', 'est_en_vedette')
    list_filter   = ('region', 'est_ouvert', 'est_en_vedette')
    search_fields = ('nom', 'ville', 'description')
    prepopulated_fields = {'slug': ('nom',)}
    list_editable = ('est_ouvert', 'est_en_vedette')
    fieldsets = (
        ('Identité',       {'fields': ('nom', 'slug', 'region', 'ville', 'adresse')}),
        ('Médias',         {'fields': ('image', 'couleur_bg')}),
        ('Description',    {'fields': ('description', 'description_courte')}),
        ('Infos pratiques',{'fields': ('nombre_boutiques', 'nombre_places_parking', 'heure_ouverture','heure_fermeture', 'telephone', 'email', 'site_web')}),
        ('Statut',         {'fields': ('est_ouvert', 'est_en_vedette', 'ouverture_prevue', 'badge')}),
    )


@admin.register(Magasin)
class MagasinAdmin(admin.ModelAdmin):
    list_display = ('nom', 'mall', 'categorie', 'localisation', 'est_en_vedette')
    list_filter = ('mall', 'categorie', 'est_en_vedette')
    search_fields = ('nom', 'description')
    prepopulated_fields = {'slug': ('nom',)}

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('titre',  'magasin', 'date_debut', 'date_fin')
    list_filter = ('magasin', 'date_debut')
    search_fields = ('titre', 'description')


@admin.register(Evenement)
class EvenementAdmin(admin.ModelAdmin):
    list_display = ('titre', 'mall', 'date', 'lieu')
    list_filter = ('mall', 'date')
    search_fields = ('titre', 'description')
    prepopulated_fields = {'slug': ('titre',)}

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('nom', 'mall',  'email', 'sujet', 'cree_le')
    readonly_fields = ('cree_le',)
    list_filter = ('mall', 'cree_le')
    search_fields = ('nom', 'email', 'sujet', 'message')

@admin.register(ArticleBlog)
class ArticleBlogAdmin(admin.ModelAdmin):
    list_display = ('titre', 'mall', 'date_publication')
    search_fields = ('titre', 'contenu')
    prepopulated_fields = {'slug': ('titre',)}

