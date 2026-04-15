from django.contrib import admin
from .models import Mall, Shop, Event, Promotion, ContactMessage, ArticleBlog


@admin.register(Mall)
class MallAdmin(admin.ModelAdmin):
    list_display  = ('name', 'city', 'region', 'number_of_shops','number_of_parking_spaces', 'is_open', 'is_featured')
    list_filter   = ('region', 'is_open', 'is_featured')
    search_fields = ('name', 'city', 'description')
    prepopulated_fields = {'slug': ('name',)}   
    list_editable = ('is_open', 'is_featured')
    fieldsets = (
        ('Identity',       {'fields': ('name', 'slug', 'region', 'city', 'address')}),
        ('Médias',         {'fields': ('image', 'bg_color')}),
        ('Description',    {'fields': ('description', 'short_description')}),
        ('Infos pratiques',{'fields': ('number_of_shops', 'number_of_parking_spaces', 'opening_time','closing_time', 'phone', 'email', 'website')}),
        ('Statut',         {'fields': ('is_open', 'is_featured', 'opening_date', 'badge')}),
    )


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'mall', 'category', 'location', 'is_featured')
    list_filter = ('mall', 'category', 'is_featured')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title',  'shop', 'start_date', 'end_date')
    list_filter = ('shop', 'start_date')
    search_fields = ('title', 'description')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'mall', 'date', 'location')
    list_filter = ('mall', 'date')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(ArticleBlog)
class ArticleBlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'mall', 'date_publication')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'mall',  'email', 'subject', 'created_at')
    readonly_fields = ('created_at',)
    list_filter = ('mall', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
