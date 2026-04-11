from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from .models import Mall,Magasin, Evenement, Promotion, ArticleBlog, ContactMessage
from .forms import MallForm,ContactForm
from django.urls import reverse_lazy
from django.contrib import messages

from django.utils import timezone


# ================ Start Home views ==========================

class HomeView(TemplateView):
    """Landing portal — display all malls."""
    template_name = 'centre_commercial/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['malls'] = Mall.objects.all()
        context['magasins_vedette'] = Magasin.objects.filter(est_en_vedette=True)[:6]
        context['evenements_prochains'] = Evenement.objects.all().order_by('date')[:3]
        context['promotions_actives'] = Promotion.objects.all().order_by('-cree_le')[:3]
        # Blog is global for now, but could be filtered too
        context['articles_blog'] = ArticleBlog.objects.all().order_by('-date_publication')[:3]
        return context

# table list mall 
class MallTableListView(ListView):
    model = Mall
    template_name = 'centre_commercial/mall_table_list.html'
    context_object_name = 'malls'

# ================ End Start Home views =======================

# ================ Start Mall views ==========================
class MallView(TemplateView):
    """Specific Mall Homepage — shows featured stores/events for a mall."""
    template_name = 'centre_commercial/mall.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mall_slug = self.kwargs.get('slug')
        mall = get_object_or_404(Mall, slug=mall_slug)
        context['mall'] = mall
        context['magasins_vedette'] = mall.magasins.all() #filter(est_en_vedette=True)[:6]
        context['evenements_prochains'] = mall.evenements.all()#.order_by('date')[:3]
        context['promotions_actives'] = Promotion.objects.filter(magasin__mall=mall).select_related('magasin')
        context['articles_blog'] = mall.blogs.all() #ArticleBlog.objects.all().order_by('-date_publication')[:3]

        restaurants_count = mall.magasins.filter(categorie='restauration').count()
        context['restaurants_count'] = restaurants_count    
        cinemas_count = mall.magasins.filter(categorie='cinema').count()
        context['cinemas_count'] = cinemas_count    

        return context  

class MallCreateView(CreateView):
    model = Mall
    form_class = MallForm
    template_name = 'centre_commercial/mall_form.html'
    success_url = reverse_lazy('home')

class MallUpdateView(UpdateView):
    model = Mall
    form_class = MallForm
    template_name = 'centre_commercial/mall_form.html'
    success_url = reverse_lazy('home')

class MallDeleteView(DeleteView):
    model = Mall
    template_name = 'centre_commercial/mall_confirm_delete.html'
    success_url = reverse_lazy('home')

# class MallDetailView(DetailView):
#     model = Mall
#     template_name = 'centre_commercial/mall_detail.html'
#     context_object_name = 'mall'

# ================ End Mall views ==========================

# ================ Start Promotion views ==========================
# class PromotionListView(ListView):
#     model = Promotion
#     template_name = 'centre_commercial/promotion_list.html'
#     context_object_name = 'promotions'
#     ordering = ['-cree_le']

class PromotionListView(ListView):
    model = Promotion
    template_name = 'centre_commercial/promotion_list.html'
    context_object_name = 'promotions'
    paginate_by = 12

    def get_queryset(self):
        now = timezone.now()

        queryset = Promotion.objects.filter(
            date_debut__lte=now,
            date_fin__gte=now
        )

        # 🎯 جلب slug من URL
        self.mall_slug = self.kwargs.get('slug')
        self.mall = None  # مهم جداً

        if self.mall_slug:
            self.mall = get_object_or_404(Mall, slug=self.mall_slug)
            queryset = queryset.filter(magasin__mall=self.mall)

        return queryset.select_related('magasin', 'magasin__mall').order_by('-cree_le')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mall'] = self.mall
        return context
# ================ End Promotion views ==========================


# ================ Start Magasin views ==========================

class MagasinListView(ListView):
    model = Magasin
    template_name = 'centre_commercial/magasin_list.html'
    context_object_name = 'magasins'
    paginate_by = 12

    def get_queryset(self):
        self.query = self.request.GET.get('q', '').strip()
        self.category = self.request.GET.get('category')
        #self.mall_slug = self.request.GET.get('mall')
        self.mall_slug = self.kwargs.get('slug')  # ✅ هنا الح

        queryset = Magasin.objects.select_related('mall')

        # ✅ filter by mall
        if self.mall_slug:
            self.mall = get_object_or_404(Mall, slug=self.mall_slug)
            queryset = queryset.filter(mall=self.mall)
        else:
            self.mall = None

        # ✅ search
        if self.query:
            queryset = queryset.filter(
                Q(nom__icontains=self.query) |
                Q(description__icontains=self.query)
            )
        # ✅ category filter
        if self.category:
            queryset = queryset.filter(categorie=self.category)
        return queryset.order_by('nom')  # 👈 ترتيب أفضل

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'categories': Magasin.CATEGORIES,
            'selected_category': self.category,
            'search_query': self.query,
            'mall': self.mall,
            'total_results': self.get_queryset().count(),  # 👈 إحصائية مفيدة
        })
        return context

class MagasinDetailView(DetailView):
    model = Magasin
    template_name = 'centre_commercial/magasin_detail.html'
    context_object_name = 'magasin'

    def get_queryset(self):
        return Magasin.objects.select_related('mall')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        magasin = self.object

        # ✅ جلب mall من URL (GET param)
        mall_slug = self.request.GET.get('mall')
        mall = None

        if mall_slug:
            mall = Mall.objects.filter(slug=mall_slug).first()

        # ✅ related magasins (من نفس المول)
        related_magasins = Magasin.objects.filter(
            mall=magasin.mall
        ).exclude(id=magasin.id).select_related('mall')[:4]

        context.update({
            'mall': mall,  # 👈 مهم للرجوع
            'related_magasins': related_magasins,
        })

        return context
# ================ End Magasin views ==========================


# ================ Start Evenement views ==========================
class EvenementListView(ListView):
    model = Evenement
    template_name = 'centre_commercial/evenement_list.html'
    context_object_name = 'evenements'
    ordering = ['-date']

    def get_queryset(self):
        self.mall_slug = self.kwargs.get('slug')
        self.mall = None

        if self.mall_slug:
            self.mall = get_object_or_404(Mall, slug=self.mall_slug)
            return Evenement.objects.filter(mall=self.mall).order_by('-date')

        return Evenement.objects.all().order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mall'] = self.mall
        return context

class EvenementDetailView(DetailView):
    model = Evenement
    template_name = 'centre_commercial/evenement_detail.html'
    context_object_name = 'evenement'
# ================ End Evenement views ==========================


# ================ Start ArticleBlog views ==========================
class ArticleBlogListView(ListView):
    model = ArticleBlog
    template_name = 'centre_commercial/blog_list.html'
    context_object_name = 'articles'
    ordering = ['-date_publication']

    def get_queryset(self):
        self.mall_slug = self.kwargs.get('slug')
        self.mall = None

        if self.mall_slug:
            self.mall = get_object_or_404(Mall, slug=self.mall_slug)
            return ArticleBlog.objects.filter(mall=self.mall).order_by('-date_publication')

        return ArticleBlog.objects.all().order_by('-date_publication')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mall'] = self.mall
        return context

class ArticleBlogDetailView(DetailView):
    model = ArticleBlog
    template_name = 'centre_commercial/blog_detail.html'
    context_object_name = 'article'
# ================ End ArticleBlog views ==========================


# ================ Start Contact views ==========================


class ContactView(CreateView):
    model = ContactMessage
    form_class = ContactForm
    template_name = 'centre_commercial/contact.html'

    def dispatch(self, request, *args, **kwargs):
        self.mall = get_object_or_404(Mall, slug=self.kwargs.get('slug'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.mall = self.mall
        form.save()

        messages.success(self.request, "Message envoyé avec succès")

        return self.render_to_response(self.get_context_data(form=self.form_class()))
# ================ End Contact views ==========================
