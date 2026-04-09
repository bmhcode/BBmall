from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from .models import Mall,Magasin, Evenement, Promotion, ArticleBlog, ContactMessage
from .forms import MallForm,ContactForm
from django.urls import reverse_lazy
from django.contrib import messages


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
        context['promotions_actives'] = mall.promotions.all()# .order_by('-cree_le')[:3]
        # Blog is global for now, but could be filtered too
        context['articles_blog'] = ArticleBlog.objects.all().order_by('-date_publication')[:3]

        restaurants_count = mall.magasins.filter(categorie='restauration').count()
        context['restaurants_count'] = restaurants_count    
        cinemas_count = mall.magasins.filter(categorie='cinema').count()
        context['cinemas_count'] = cinemas_count    

        return context  

# ================ Start Mall views ==========================
class MallListView(ListView):
    model = Mall
    template_name = 'centre_commercial/mall_list.html'
    context_object_name = 'malls'

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


# ================ Start Magasin views ==========================
class MagasinListView(ListView):
    model = Magasin
    template_name = 'centre_commercial/magasin_list.html'
    context_object_name = 'magasins'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q')
        category = self.request.GET.get('category')
        queryset = Magasin.objects.all()
        if query:
            queryset = queryset.filter(
                Q(nom__icontains=query) | Q(description__icontains=query)
            )
        if category:
            queryset = queryset.filter(categorie=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Magasin.CATEGORIES
        return context




class MagasinDetailView(DetailView):
    model = Magasin
    template_name = 'centre_commercial/magasin_detail.html'
    context_object_name = 'magasin'
# ================ End Magasin views ==========================


# ================ Start Evenement views ==========================
class EvenementListView(ListView):
    model = Evenement
    template_name = 'centre_commercial/evenement_list.html'
    context_object_name = 'evenements'
    ordering = ['-date']

class EvenementDetailView(DetailView):
    model = Evenement
    template_name = 'centre_commercial/evenement_detail.html'
    context_object_name = 'evenement'
# ================ End Evenement views ==========================


# ================ Start Promotion views ==========================
class PromotionListView(ListView):
    model = Promotion
    template_name = 'centre_commercial/promotion_list.html'
    context_object_name = 'promotions'
    ordering = ['-cree_le']
# ================ End Promotion views ==========================


# ================ Start ArticleBlog views ==========================
class ArticleBlogListView(ListView):
    model = ArticleBlog
    template_name = 'centre_commercial/blog_list.html'
    context_object_name = 'articles'
    ordering = ['-date_publication']

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
    success_url = reverse_lazy('contact')

    def form_valid(self, form):
        messages.success(self.request, "Votre message a été envoyé avec succès !")
        return super().form_valid(form)
# ================ End Contact views ==========================
