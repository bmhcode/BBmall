from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

import uuid
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError


from django.utils.html import mark_safe
from django_ckeditor_5.fields import CKEditor5Field
from django.conf import settings


def user_directory_path(instance,filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class Mall(models.Model):
    """Centre commercial — modèle principal du portail."""
    CITIES = [
        ('constantine', 'Constantine'),
        ('alger','Alger'),
        ('oran','Oran'),
        ('annaba','Annaba'),
        ('setif','Sétif'),
        ('autre','Autre'),
    ]
    # ── Identité ──
    name        = models.CharField(max_length=200, verbose_name="Name of mall")
    slug       = models.SlugField(unique=True, blank=True)
    city      = models.CharField(max_length=50, choices=CITIES, verbose_name="City")
    region     = models.CharField(max_length=100, verbose_name="Region")
    address    = models.CharField(max_length=300, verbose_name="Full address")

    # ── Médias ──
    image      = models.ImageField(upload_to='malls/', blank=True, null=True, verbose_name="Image principale")
    color_bg = models.CharField(max_length=200, default="linear-gradient(135deg,#1a1a2e,#2d1f6e)",
                                  verbose_name="Gradient CSS (fallback image)",
                                  help_text="Ex: linear-gradient(135deg,#1a1a2e,#e91e8c)")

    # ── Description ──
    description       = models.TextField(verbose_name="Description")
    description_short = models.CharField(max_length=180, blank=True, verbose_name="Short description (preview)")

    # ── Infos pratiques ──
    number_of_shops = models.PositiveIntegerField(default=0, verbose_name="Number of shops")
    number_of_parking_spaces = models.PositiveIntegerField(default=0, verbose_name="Number of parking spaces")

    opening_time = models.TimeField(default="10:00", verbose_name="Opening time")
    closing_time = models.TimeField(default="22:00", verbose_name="Closing time")

    phone        = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone")
    email            = models.EmailField(blank=True, null=True)
    website         = models.URLField(blank=True, null=True)

    # ── Statut ──
    is_open      = models.BooleanField(default=True, verbose_name="Is open ?")
    is_featured  = models.BooleanField(default=False, verbose_name="Is featured ?") 
    opening_date = models.DateField(blank=True, null=True, verbose_name="Opening date (if future)")
    badge           = models.CharField(max_length=40, blank=True, verbose_name="Badge (ex: New, Phare)")
    observation     = models.TextField(blank=True, null=True, verbose_name="Observation") # En cas de fermeture ou autre
    
    # ── Meta ──
    created_at    = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.pk:
            old = Mall.objects.get(pk=self.pk)
            if old.name != self.name:
                self.slug = slugify(self.name)
        else:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('mall_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = "Centre Commercial (Mall)"
        verbose_name_plural = "Centres Commerciaux (Malls)"
        ordering = ['-is_featured', 'name']

    
    @property
    def is_open_now(self):
        if not self.is_open:
            return False

        if not self.opening_time or not self.closing_time:
            return False

        now = timezone.localtime().time()  # 🔥 مهم

        if self.opening_time < self.closing_time:
            return self.opening_time <= now <= self.closing_time
        else:
            return now >= self.opening_time or now <= self.closing_time


class MallImage(models.Model):
    mall = models.ForeignKey(Mall, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='malls/images/')
    legende = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Image for {self.mall.name}"

class Shop(models.Model):
    CATEGORIES = [
        ('mode', 'Mode'),
        ('beaute', 'Beauté & Santé'),
        ('restauration', 'Restauration'),
        ('technologie', 'Technologie'),
        ('maison', 'Maison'),
        ('loisirs', 'Loisirs & Culture'),
        ('cinema', 'Cinéma'),
        ('autre', 'Autre'),
    ]

    # ── Relation ──
    mall = models.ForeignKey(Mall, on_delete=models.SET_NULL, null=True, blank=True, related_name='shops')

    # ── Identité ──
    name = models.CharField(max_length=200, verbose_name="Name of shop")
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORIES, verbose_name="Category")
    description = models.TextField(verbose_name="Description")
    cover = models.ImageField(upload_to='shops/cover/', verbose_name="Cover")
    logo = models.ImageField(upload_to='shops/logo/', verbose_name="Logo")

    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone")
    location = models.CharField(max_length=200, help_text="Ex: Niveau 1, Aile Nord", verbose_name="Location")
    website = models.URLField(blank=True, null=True, verbose_name="Website")
    is_featured = models.BooleanField(default=False, verbose_name="Is featured ?")

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_closed = models.BooleanField(default=False, verbose_name="Is closed ?")
    observation = models.TextField(blank=True, null=True, verbose_name="Observation") # En cas de fermeture ou autre


    class Meta:
        verbose_name = "Shop"
        verbose_name_plural = "Shops"

    def __str__(self):
        return f"{self.mall.name if self.mall else 'Without mall'} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('magasin_detail', kwargs={'slug': self.slug})
        # return reverse('magasin_detail_by_mall', kwargs={'mall_slug': self.mall.slug, 'slug': self.slug})

    
    @property
    def logoURL(self):
        return self.logo.url if self.logo else ""

    @property
    def coverURL(self):
        return self.cover.url if self.cover else ""

    @property
    def localisation(self):
        if self.mall.city and self.mall.region:
            return f"{self.mall.city}, {self.mall.region} - {self.localisation}"
        elif self.mall.city:
            return self.mall.city - {self.localisation}
        elif self.mall.region:
            return self.mall.region - {self.localisation}
        return "No location"

    def is_open_now(self):
        # 1. Manual override
        if self.is_closed:
            return False

        now = timezone.now()
        today = now.date()
        time_now = now.time()

        # 2. Check for Holidays
        if self.holidays.filter(date_begin__lte=today, date_end__gte=today).exists():
            return False

        # 3. Check Working Hours
        day = today.weekday()
        working = self.working_hours.filter(day=day, is_closed=False).first()

        if working:
            return working.open_time <= time_now <= working.close_time
        return False


class Promotion(models.Model):
    # ── Relation ──
    # Note: Promotion already has a FK to Magasin, which has a FK to Mall.
    # But adding a direct FK to Mall can optimize queries and allow mall-wide promos.
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='promotions')
   
    title = models.CharField(max_length=200, verbose_name="Title")
    description = models.TextField(verbose_name="Description")
    image = models.ImageField(upload_to='promotions/', verbose_name="Image")
    start_date = models.DateField(verbose_name="Start date")
    end_date = models.DateField(verbose_name="End date")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")

    def __str__(self):
        return f"{self.title} - {self.shop.name}"

    class Meta:
        verbose_name = "Promotion"
        verbose_name_plural = "Promotions"

class Event(models.Model):
    # ── Relation ──
    mall = models.ForeignKey(Mall, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')

    title = models.CharField(max_length=200, verbose_name="Title")
    slug = models.SlugField(unique=True, blank=True)
    date = models.DateTimeField(verbose_name="Date")
    description = models.TextField(verbose_name="Description")
    image = models.ImageField(upload_to='events/', verbose_name="Image")
    location = models.CharField(max_length=200, default="Place Centrale", verbose_name="Location")
    created_at = models.DateTimeField(auto_now_add=True)

    start_event = models.DateTimeField(verbose_name="Start event")
    end_event = models.DateTimeField(verbose_name="End event")

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
    
    def __str__(self):
        return f"{self.title} ({self.mall.name if self.mall else 'Without mall'})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'slug': self.slug})
        # return reverse('evenement_detail_by_mall', kwargs={'mall_slug': self.mall.slug, 'slug': self.slug})

class ArticleBlog(models.Model):
    # ── Relation ──
    mall = models.ForeignKey(Mall, on_delete=models.SET_NULL, null=True, blank=True, related_name='blogs')

    title = models.CharField(max_length=200, verbose_name="Title")
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField(verbose_name="Content")
    image = models.ImageField(upload_to='blog/', verbose_name="Image")
    date_publication = models.DateTimeField(auto_now_add=True, verbose_name="Date publication")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = "Blog Article"
        verbose_name_plural = "Blog Articles"


class ContactMessage(models.Model):
    # ── Relation ──
    mall = models.ForeignKey(Mall, on_delete=models.SET_NULL, null=True, blank=True, related_name='contacts')

    name = models.CharField(max_length=100, verbose_name="Name")
    email = models.EmailField(verbose_name="Email")
    subject = models.CharField(max_length=200, verbose_name="Subject")
    message = models.TextField(verbose_name="Message")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date created")

    def __str__(self):
        return f"Message de {self.name} - {self.subject}"


class NewsFeed(models.Model): # Fil d'actualités
    # ── Relation ──
    mall = models.ForeignKey(Mall, on_delete=models.SET_NULL, null=True, blank=True, related_name='fils_actualites')

    title = models.CharField(max_length=200, verbose_name="Title")
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField(verbose_name="Content")
    image = models.ImageField(upload_to='fils_actualites/', verbose_name="Image")
    start_publication = models.DateTimeField(auto_now_add=True, verbose_name="Start publication")
    end_publication = models.DateTimeField(verbose_name="End publication")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news_feed_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = "News Feed"
        verbose_name_plural = "News Feeds"


class MallVideo(models.Model):
    mall = models.ForeignKey(Mall, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='malls/videos/')
    legende = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Video for {self.mall.name}"    

#============== Start Paneau d'affichage ==============
class DisplayBoard(models.Model): # Paneau d'affichage
    # ── Relation ──
    mall = models.ForeignKey(Mall, on_delete=models.SET_NULL, null=True, blank=True, related_name='display_boards')

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='display_boards/')
    start_publication = models.DateTimeField(auto_now_add=True)
    end_publication = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('display_board_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = "Display Board"
        verbose_name_plural = "Display Boards"
#============== End Paneau d'affichage ==============

#============================
   # Start Shopping
#============================
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')

    phone = models.CharField(max_length=20, blank=True, null=True)
    # image = CloudinaryField("image", blank=True, null=True)
    image = models.ImageField(upload_to="profile/", blank=True, null=True)
    is_seller = models.BooleanField(default=False)
    is_validated = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    observation = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.user.username

    @property
    def imageURL(self):
        return self.image.url if self.image else ""


class Store(models.Model):
    name    = models.CharField('name of store', max_length=255, blank=True, null=False, default="BB Shopping")
    about_us = CKEditor5Field('Text', config_name='extends')
    address = models.CharField(max_length=255, blank=True, null=True, default="Store adress")
    phone  = models.CharField('Contact Phone',max_length=255, blank=True, null=True, default="Store phone")
    email  = models.EmailField('Email Address', max_length=255, default="store@mail.com")
    logo   = models.ImageField(upload_to="store/", blank=True, default='', )
    # logo = CloudinaryField('logo', blank=True, null=True)
    web = models.URLField('Website Adress',null=True, blank=True)

    def __str__(self):
        return self.name
    
    @property
    def logoURL(self):
        try:
            url = self.logo.url
        except:
            url = ''
        return url
    
class StoreSection(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=50)
    subtitle = models.CharField(max_length=50)
    description = CKEditor5Field('Text', config_name='extends')
    image = models.ImageField(upload_to="store_sections/", blank=True, default='', )

    def __str__(self):
        return self.title
    
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

class Subscription(models.Model):

    PLAN_CHOICES = (
        ('FREE', 'Free'),
        ('PRO', 'Pro'),
        ('BUSINESS', 'Business'),
    )

    PLAN_LIMITS = {
        'FREE': 3,
        'PRO': 5,
        'BUSINESS': None,  # None = Unlimited
    }

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='FREE')

    def max_products(self):
        return self.PLAN_LIMITS.get(self.plan)

    def __str__(self):
        return f"{self.user.username} - {self.plan}"

class Brand(models.Model):
    name = models.CharField(
        max_length=128,
        unique=True,
        verbose_name=_("Name of brand"),
        db_index=True
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
        max_length=160
    )

    image = models.ImageField(upload_to="brands/", blank=True, null=True)
    # image = CloudinaryField(
    #     "image",
    #     blank=True,
    #     null=True
    # )

    start_date = models.DateTimeField(
        verbose_name=_("Start at"),
        default=timezone.now
    )

    end_date = models.DateTimeField(
        verbose_name=_("End at"),
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date"]
        verbose_name = _("Brand")
        verbose_name_plural = _("Brands")

    def __str__(self):
        return self.name

    # 🔹 slug auto-generate (clean + safe)
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)

            # prevent duplicates
            slug = base_slug
            while Brand.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"

            self.slug = slug

        super().save(*args, **kwargs)

    # 🔹 safe image URL
    @property
    def imageURL(self):
        if self.image:
            return self.image.url
        return ""

    # 🔹 check if brand is currently active (based on date)
    @property
    def is_current(self):
        now = timezone.now()
        if self.end_date:
            return self.start_date <= now <= self.end_date
        return self.start_date <= now


class ProductCategory(models.Model):
    name   = models.CharField(unique=True, max_length=100, verbose_name=_("Product category")) #,default='name of the category', help_text='name of catygory')
    slug   = models.SlugField(blank=True,null=True, unique=True)

    image = models.ImageField(upload_to="Product/categories/", blank=True, null=True)
    # image = CloudinaryField('image', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural= 'Product categories'
      
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) + "-" + str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)            
      
    def get_absolute_url(self):
        return reverse('index')
        # return 'https://www.google.fr'
    
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    
    def my_image(self):
        if self.image:
            return mark_safe(f'<img src="{self.image.url}" width="50" height="50" />')
        return "-"    

# ============ / End Category
  
class ShopHoliday(models.Model):
    shop       = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='holidays')
    name       = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date   = models.DateField()

    def __str__(self):
        return f"{self.shop.name} - {self.name}"

class MagasinSocial(models.Model):
    shop = models.OneToOneField(Shop, on_delete=models.CASCADE, related_name='social')

    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    tiktok = models.URLField(blank=True)
    whatsapp = models.URLField(blank=True)
    telegram = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
   
class ShopValidation(models.Model):
    PERIOD_CHOICES = [
        (30, '1 Month'),
        (90, '3 Months'),
        (180, '6 Months'),
        (365, '1 Year'),
    ]

    shop = models.OneToOneField(Shop, on_delete=models.CASCADE, related_name='validation')

    is_validated = models.BooleanField(default=False)
  
    observation = models.TextField(blank=True)

    start_date = models.DateField(null=True, blank=True,verbose_name=_("Start date"))
    period = models.IntegerField(choices=PERIOD_CHOICES, null=True, blank=True,verbose_name=_("Period"))

    def is_active(self):
        if self.start_date and self.period:
            from datetime import timedelta
            return self.start_date + timedelta(days=self.period)
        return None    


# ============ / End Shop =================

class Product(models.Model):
    shop     = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True , related_name='products')
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    name     = models.CharField(unique=True, max_length=128, verbose_name =_('Name of product'))
    slug     = models.SlugField(unique=True)
    old_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True,null=True, verbose_name =_('Old price'))
    price    = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True,null=True)
    description = CKEditor5Field('Text', config_name='extends')

    image = models.ImageField(upload_to="products/", blank=True, null=True)
    # image = CloudinaryField('image', blank=True, null=True)

    created_at  = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at  = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    is_featured = models.BooleanField(default=False)

    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = _("Product")
        # verbose_name_plural = _("Products")
    
    def __str__(self):
        return  f"{self.name}" # ({self.description[0:50]})"
      
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) + "-" + str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)
            
    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"slug": self.slug})
        # return reverse('index')
        # return 'https://www.google.fr'

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    
    # Adminلعرض صورة مصغرة في 
    def product_image(self):
        if self.image:
            return mark_safe('<img src="%s" width="50" height="50"/>' % self.image.url)
        return "-"  

    @property
    def user_phone(self):
        if hasattr(self.shop.user, "profile"):
            return self.shop.user.profile.phone
        return None

    @property
    def is_new(self):
        """يرجع True إذا المنتج تم إنشاؤه منذ أقل من 1 أيام"""
        return timezone.now() - self.created_at <= timedelta(days=1)

    product_image.short_description = 'Image'

    def get_precentage(self):
        new_price = (self.price / self.old_price) * 100
        return new_price

    @property
    def main_image(self):
        first = self.images.first()
        if first:
            return first.image.url
        return ""
    
class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True,related_name='images', verbose_name=_("Product images"))
    caption = models.CharField(max_length=128, blank=True, null=True)
    image = models.ImageField(upload_to="products/images/", blank=True, null=True)
    # image   = CloudinaryField('image', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    order = models.PositiveIntegerField(default=0) 

    class Meta:
        verbose_name_plural = _("Product images") 
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Image of {self.product.name} - {self.id}"
      
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

class Wishlist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')

    products = models.ManyToManyField(Product, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist for {self.user.username}"

# =========================
# SALES MODEL
# =========================
class Sale(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sales")
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)

    # ✅ TRANSACTION AMOUNT
    transaction_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True)
    # ✅ TRANSACTION RATIO (commission %)
    transaction_ratio = models.DecimalField(max_digits=5,decimal_places=2,default=0.00,help_text="Percentage (%)")
    profit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def save(self, *args, **kwargs):
        # auto slug
        if not self.slug:
            self.slug = slugify(self.title) + "-" + str(uuid.uuid4())[:6]

        # calculate profit
        self.profit = self.transaction_amount * self.transaction_ratio/100

        super().save(*args, **kwargs)

# ===================================================================================================================
# START ORDER MODEL
# ===================================================================================================================

class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash on Delivery'),
        ('card', 'Card'),
        ('transfer', 'Bank Transfer'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)

    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    address = models.CharField(max_length=255)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    # -----------------------------
    # حساب السعر الإجمالي
    # -----------------------------
    def update_total_price(self):
        total = sum(
            item.quantity * item.price
            for item in self.items.all()
        )
        self.total_price = total
        self.save(update_fields=['total_price'])

    # -----------------------------
    # تحديث الحالة من العناصر
    # -----------------------------


    def update_status_from_items(self):
        statuses = list(self.items.values_list('status', flat=True))

        if not statuses:
            return

        if all(s == 'received' for s in statuses):
            new_status = 'delivered'

        elif all(s == 'cancelled' for s in statuses):
            new_status = 'cancelled'

        elif any(s == 'processing' for s in statuses):
            new_status = 'processing'

        elif any(s == 'available' for s in statuses):
            new_status = 'shipped'

        else:
            new_status = 'pending'

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=['status'])

    def propagate_status_to_items(self, user=None):
        item_status_map = {
            'pending': 'processing',
            'processing': 'processing',
            'shipped': 'available',
            'delivered': 'received',
            'cancelled': 'cancelled'
        }
        new_item_status = item_status_map.get(self.status)
        if new_item_status:
            for item in self.items.all():
                if item.status != new_item_status:
                    old_item_status = item.status
                    item.status = new_item_status
                    item.save(update_fields=['status'])
                    OrderItemHistory.objects.create(
                        order_item=item,
                        old_status=old_item_status,
                        new_status=new_item_status,
                        changed_by=user
                    )

#----------------------------- Order Item Model ----------------------------------
class OrderItem(models.Model):

    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('available', 'Available'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]

    order    = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product  = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price    = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.product} x {self.quantity}"

    @property
    def get_total(self):
        return self.quantity * self.price

class OrderItemHistory(models.Model):
    order_item = models.ForeignKey('OrderItem', on_delete=models.CASCADE, related_name='history')
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Status changed from {self.old_status} to {self.new_status} for {self.item}"

class OrderHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='history')
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.order.id}: {self.old_status} → {self.new_status}"


# =========================
#  END ORDER MODEL
# =========================

class ShopReview(models.Model): # Shop Review Model
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    rating = models.IntegerField(default=5)  # من 1 إلى 5
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('shop', 'user')  # user يقيّم مرة واحدة فقط

#============== End Shopping ==============
