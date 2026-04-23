from django.contrib import admin
from django.utils.html import format_html
from .models import Profile, Subscription, Mall, Shop, Event, Promotion, ContactMessage, ArticleBlog, Product, ProductImages, ProductCategory

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# ═════════════════════════════════════════════════════════════
# INLINES
# ═════════════════════════════════════════════════════════════

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'


class SubscriptionInline(admin.StackedInline):
    model = Subscription
    can_delete = False
    verbose_name_plural = 'Subscription'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, SubscriptionInline)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class ShopInline(admin.TabularInline):
    model = Shop
    extra = 1
    fields = ('owner', 'name', 'category', 'location', 'is_featured')
    # prepopulated_fields = {'slug': ('name',)}

class ProductImageInline(admin.TabularInline):
    model = ProductImages
    extra = 3
    fields = ('image', 'caption', 'order')

# ═════════════════════════════════════════════════════════════
# MODEL ADMINS
# ═════════════════════════════════════════════════════════════

@admin.register(Mall)
class MallAdmin(admin.ModelAdmin):
    list_display = ('get_thumbnail', 'manager', 'name', 'city', 'region', 'number_of_shops', 'is_open', 'is_featured')
    list_filter = ('city', 'region', 'is_open', 'is_featured')
    search_fields = ('name', 'city', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_open', 'is_featured')
    inlines = [ShopInline]
    
    fieldsets = (
        ('Identité',      {'fields': ('manager', 'name', 'slug', 'city', 'region', 'address')}),
        ('Médias',        {'fields': ('image', 'bg_color')}),
        ('Description',   {'fields': ('description', 'description_short')}),
        ('Infos Pratiques', {'fields': ('number_of_shops', 'number_of_parking_spaces', 'opening_time', 'closing_time', 'phone', 'email', 'website')}),
        ('Statut',        {'fields': ('is_open', 'is_featured', 'opening_date', 'badge')}),
    )

    def get_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 35px; object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return "-"
    get_thumbnail.short_description = 'Aperçu'

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('get_thumbnail', 'owner', 'name', 'mall', 'category', 'location', 'is_featured')
    list_filter = ('mall', 'category', 'is_featured')
    search_fields = ('name', 'description')
    # prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_featured',)

    fieldsets = (
        ('Identité',      {'fields': ('owner', 'name', 'mall', 'category', 'location')}),
        ('Design',        {'fields': ('logo', 'cover', 'description')}),
        ('Contact',       {'fields': ('phone', 'email', 'website')}),
        ('Paramètres',    {'fields': ('is_featured', 'is_closed', 'observation')}),
    )

    def get_thumbnail(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 50%;" />', obj.logo.url)
        return "-"
    get_thumbnail.short_description = 'Logo'

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('get_thumbnail', 'name', 'shop', 'category', 'price', 'old_price', 'created_at')
    list_filter = ('shop__mall', 'category', 'shop')
    search_fields = ('name', 'shop__name')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('price', 'old_price')
    inlines = [ProductImageInline]

    def get_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 45px; height: 45px; object-fit: cover; border-radius: 8px;" />', obj.image.url)
        return "-"
    get_thumbnail.short_description = 'Aperçu'

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'shop', 'start_date', 'end_date')
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
    list_display = ('name', 'mall', 'email', 'subject', 'created_at')
    readonly_fields = ('created_at',)
    list_filter = ('mall', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
