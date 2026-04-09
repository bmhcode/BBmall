from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Mall(models.Model):
    """Centre commercial — modèle principal du portail."""

    VILLES = [
        ('constantine', 'Constantine'),
        ('alger',       'Alger'),
        ('oran',        'Oran'),
        ('annaba',      'Annaba'),
        ('setif',       'Sétif'),
        ('autre',       'Autre'),
    ]

    # ── Identité ──
    nom        = models.CharField(max_length=200, verbose_name="Nom du mall")
    slug       = models.SlugField(unique=True, blank=True)
    ville      = models.CharField(max_length=50, choices=VILLES, verbose_name="Ville")
    region     = models.CharField(max_length=100, verbose_name="Région")
    adresse    = models.CharField(max_length=300, verbose_name="Adresse complète")

    # ── Médias ──
    image      = models.ImageField(upload_to='malls/', blank=True, null=True, verbose_name="Image principale")
    couleur_bg = models.CharField(max_length=200, default="linear-gradient(135deg,#1a1a2e,#2d1f6e)",
                                  verbose_name="Gradient CSS (fallback image)",
                                  help_text="Ex: linear-gradient(135deg,#1a1a2e,#e91e8c)")

    # ── Description ──
    description      = models.TextField(verbose_name="Description")
    description_courte = models.CharField(max_length=180, blank=True, verbose_name="Description courte (aperçu)")

    # ── Infos pratiques ──
    nombre_boutiques = models.PositiveIntegerField(default=0, verbose_name="Nombre de boutiques")
    nombre_places_parking = models.PositiveIntegerField(default=0, verbose_name="Nombre de places de parking")

    horaires         = models.CharField(max_length=100, default="10h – 22h", verbose_name="Horaires d'ouverture")
    telephone        = models.CharField(max_length=20, blank=True, null=True)
    email            = models.EmailField(blank=True, null=True)
    site_web         = models.URLField(blank=True, null=True)

    # ── Statut ──
    est_ouvert      = models.BooleanField(default=True, verbose_name="Ouvert ?")
    est_en_vedette  = models.BooleanField(default=False, verbose_name="Mis en avant ?")
    ouverture_prevue = models.DateField(blank=True, null=True, verbose_name="Date d'ouverture prévue (si futur)")
    badge           = models.CharField(max_length=40, blank=True, verbose_name="Badge (ex: Nouveau, Phare)")

    # ── Meta ──
    cree_le    = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.pk:
            old = Mall.objects.get(pk=self.pk)
            if old.nom != self.nom:
                self.slug = slugify(self.nom)
        else:
            self.slug = slugify(self.nom)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('mall_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = "Centre Commercial (Mall)"
        verbose_name_plural = "Centres Commerciaux (Malls)"
        ordering = ['-est_en_vedette', 'nom']


class Magasin(models.Model):
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
    mall = models.ForeignKey(Mall, on_delete=models.SET_NULL, null=True, blank=True, related_name='magasins')

    # ── Identité ──
    nom = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    categorie = models.CharField(max_length=50, choices=CATEGORIES)
    description = models.TextField()
    image = models.ImageField(upload_to='magasins/')
    localisation = models.CharField(max_length=200, help_text="Ex: Niveau 1, Aile Nord")
    site_web = models.URLField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    est_en_vedette = models.BooleanField(default=False)
    cree_le = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} ({self.mall.nom if self.mall else 'Sans centre'})"

    def get_absolute_url(self):
        return reverse('magasin_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = "Magasin"
        verbose_name_plural = "Magasins"


class Evenement(models.Model):
    # ── Relation ──
    mall = models.ForeignKey(Mall, on_delete=models.SET_NULL, null=True, blank=True, related_name='evenements')

    titre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    date = models.DateTimeField()
    description = models.TextField()
    image = models.ImageField(upload_to='evenements/')
    lieu = models.CharField(max_length=200, default="Place Centrale")
    cree_le = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.titre} ({self.mall.nom if self.mall else 'Sans centre'})"

    def get_absolute_url(self):
        return reverse('evenement_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = "Événement"
        verbose_name_plural = "Événements"


class Promotion(models.Model):
    # ── Relation ──
    # Note: Promotion already has a FK to Magasin, which has a FK to Mall.
    # But adding a direct FK to Mall can optimize queries and allow mall-wide promos.
    mall = models.ForeignKey(Mall, on_delete=models.SET_NULL, null=True, blank=True, related_name='promotions')
    
    titre = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='promotions/')
    date_debut = models.DateField()
    date_fin = models.DateField()
    magasin = models.ForeignKey(Magasin, on_delete=models.CASCADE, related_name='promotions')
    cree_le = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titre} - {self.magasin.nom}"

    class Meta:
        verbose_name = "Promotion"
        verbose_name_plural = "Promotions"


class ContactMessage(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    sujet = models.CharField(max_length=200)
    message = models.TextField()
    cree_le = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message de {self.nom} - {self.sujet}"


class ArticleBlog(models.Model):
    titre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    contenu = models.TextField()
    image = models.ImageField(upload_to='blog/')
    date_publication = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = "Article de Blog"
        verbose_name_plural = "Articles de Blog"

