from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from .models import Mall,Shop, Event, Promotion, ArticleBlog, ContactMessage
from .forms import MallForm,ContactForm
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.utils import timezone

# ================ Start Home views ==========================
class HomeView(TemplateView):
    """Landing portal — display all malls."""
    template_name = 'centre_commercial/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['malls'] = Mall.objects.all()
        context['shops_featured'] = Shop.objects.filter(is_featured=True)[:6]
        context['future_events'] = Event.objects.filter(end_event__gt=timezone.now()).order_by('start_event')[:3]
        context['active_promotions'] = Promotion.objects.filter(end_date__gt=timezone.now()).order_by('-created_at')[:3]
        # Blog is global for now, but could be filtered too
        context['blogs'] = ArticleBlog.objects.all().order_by('-date_publication')[:3]
        return context

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
        context['shops_featured'] = mall.shops.all() #filter(is_featured=True)[:6]
        context['future_events'] = mall.events.all()#.order_by('date')[:3]
        context['promotions_actives'] = Promotion.objects.filter(shop__mall=mall).select_related('shop')
        context['articles_blog'] = mall.blogs.all() #ArticleBlog.objects.all().order_by('-date_publication')[:3]

        restaurants_count = mall.shops.filter(category='restauration').count()
        context['restaurants_count'] = restaurants_count    
        cinemas_count = mall.shops.filter(category='cinema').count()
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
class PromotionListView(ListView):
    model = Promotion
    template_name = 'centre_commercial/promotion_list.html'
    context_object_name = 'promotions'
    paginate_by = 12

    def get_queryset(self):
        now = timezone.now()

        queryset = Promotion.objects.filter(
            start_date__lte=now,
            end_date__gte=now
        )

        # 🎯 جلب slug من URL
        self.mall_slug = self.kwargs.get('slug')
        self.mall = None  # مهم جداً

        if self.mall_slug:
            self.mall = get_object_or_404(Mall, slug=self.mall_slug)
            queryset = queryset.filter(shop__mall=self.mall)

        return queryset.select_related('shop', 'shop__mall').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mall'] = self.mall
        return context
# ================ End Promotion views ==========================


# ================ Start Magasin views ==========================
class ShopListView(ListView):
    model = Shop
    template_name = 'centre_commercial/shop_list.html'
    context_object_name = 'shops'
    paginate_by = 12

    def get_queryset(self):
        self.query = self.request.GET.get('q', '').strip()
        self.category = self.request.GET.get('category')
        #self.mall_slug = self.request.GET.get('mall')
        self.mall_slug = self.kwargs.get('slug')  # ✅ هنا الح

        queryset = Shop.objects.select_related('mall')

        # ✅ filter by mall
        if self.mall_slug:
            self.mall = get_object_or_404(Mall, slug=self.mall_slug)
            queryset = queryset.filter(mall=self.mall)
        else:
            self.mall = None

        # ✅ search
        if self.query:
            queryset = queryset.filter(
                Q(name__icontains=self.query) |
                Q(description__icontains=self.query)
            )
        # ✅ category filter
        if self.category:
            queryset = queryset.filter(category=self.category)
        return queryset.order_by('name')  # 👈 ترتيب أفضل

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'categories': Shop.CATEGORIES,
            'selected_category': self.category,
            'search_query': self.query,
            'mall': self.mall,
            'total_results': self.get_queryset().count(),  # 👈 إحصائية مفيدة
        })
        return context

class ShopDetailView(DetailView):
    model = Shop
    template_name = 'centre_commercial/shop_detail.html'
    context_object_name = 'shop'

    def get_queryset(self):
        # ⚡ تحسين الأداء (join مع mall)
        return Shop.objects.select_related('mall')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shop = self.object

        # ✅ المول مباشرة من العلاقة
        mall = shop.mall

        # ✅ متاجر من نفس المول
        related_shops = (
            Shop.objects
            .filter(mall=mall)
            .exclude(id=shop.id)
            .select_related('mall')[:4]
        )

        context.update({
            'mall': mall,  # 👈 الآن مضمون دائماً
            'related_shops': related_shops,
        })

        return context
# ================ End Magasin views ==========================


# ================ Start Evenement views ==========================
class EventListView(ListView):
    model = Event
    template_name = 'centre_commercial/event_list.html'
    context_object_name = 'events'
    ordering = ['-date']

    def get_queryset(self):
        self.mall_slug = self.kwargs.get('slug')
        self.mall = None

        if self.mall_slug:
            self.mall = get_object_or_404(Mall, slug=self.mall_slug)
            return Event.objects.filter(mall=self.mall).order_by('-date')

        return Event.objects.all().order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mall'] = self.mall
        return context

class EventDetailView(DetailView):
    model = Event
    template_name = 'centre_commercial/event_detail.html'
    context_object_name = 'event'

    def get_object(self):
        return get_object_or_404(
            Event,
            slug=self.kwargs['slug'],
            mall__slug=self.kwargs['mall_slug']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mall'] = self.object.mall
        return context
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

    def get_object(self):
        return get_object_or_404(
            ArticleBlog,
            slug=self.kwargs['slug'],
            mall__slug=self.kwargs['mall_slug']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mall'] = self.object.mall
        return context
# ================ End ArticleBlog views ==========================


# ================ Start Contact views ==========================

class ContactCreateView(CreateView):
    model = ContactMessage
    form_class = ContactForm
    template_name = 'centre_commercial/contact.html'

    def dispatch(self, request, *args, **kwargs):
        self.mall = get_object_or_404(Mall, slug=self.kwargs.get('mall_slug'))  # ✅
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.mall = self.mall
        form.save()

        messages.success(self.request, "Message envoyé avec succès")

        return redirect('mall', self.mall.slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mall'] = self.mall  # ✅ أفضل
        return context


class ContactListView(ListView):
    model = ContactMessage
    template_name = 'centre_commercial/contacts_messages_list.html'
    context_object_name = 'contacts'

    def get_queryset(self):
        self.mall_slug = self.kwargs.get('mall_slug')  # ✅ التصحيح هنا
        self.mall = None

        if self.mall_slug:
            self.mall = get_object_or_404(Mall, slug=self.mall_slug)
            return ContactMessage.objects.filter(mall=self.mall).order_by('-created_at')

        return ContactMessage.objects.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mall'] = get_object_or_404(Mall, slug=self.kwargs['mall_slug'])
        return context

class ContactDetailView(DetailView):
    model = ContactMessage
    template_name = 'centre_commercial/contact_message_detail.html'
    context_object_name = 'contact'

    def get_object(self):
        return get_object_or_404(ContactMessage, id=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mall'] = self.object.mall
        return context

class ContactDeleteView(DeleteView):
    model = ContactMessage
    template_name = 'centre_commercial/contact_message_delete.html'
    context_object_name = 'contact'

    def get_object(self):
        return get_object_or_404(ContactMessage, id=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mall'] = self.object.mall
        return context  

    def get_success_url(self):
        return reverse('contacts_by_mall', kwargs={
        'mall_slug': self.object.mall.slug
    })

# ================ End Contact views ==========================
