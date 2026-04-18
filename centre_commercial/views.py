from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.db.models import Q,Sum
from .models import Profile, Mall,Shop, Event, Promotion, ArticleBlog, ContactMessage, Product, ProductImages
from .forms import UserUpdateForm, ProfileUpdateForm,MallForm, ShopForm, ContactForm, ProductForm
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.utils import timezone


from django.contrib.auth.forms import UserCreationForm
# from .forms import OrderUpdateForm, OrderItemFormSet

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User



#--------------------- Auth --------------------------------
def signup(request): # signup
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    
    context = {
            'form': form
    }
    return render(request, 'registration/signup.html', context)

@login_required # update_profile
def update_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile, _ = Profile.objects.get_or_create(user=user)
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=user)
        p_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=profile
        )
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('home')
    else:
        u_form = UserUpdateForm(instance=user)
        p_form = ProfileUpdateForm(instance=profile)

    context = {
        'user': user,
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'registration/update_profile.html', context)
#--------------------- / Auth --------------------------------


# ================ Start Home views ==========================
class HomeView(TemplateView):
    """Landing portal — display all malls."""
    template_name = 'mall/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['malls'] = Mall.objects.all()
        context['number_of_shops'] = Mall.objects.aggregate(total=Sum('number_of_shops'))['total'] or 0
        context['shops_featured'] = Shop.objects.filter(is_featured=True)[:6]
        context['future_events'] = Event.objects.filter(end_event__gt=timezone.now()).order_by('start_event')[:3]
        context['active_promotions'] = Promotion.objects.filter(end_date__gt=timezone.now()).order_by('-created_at')[:3]
        # Blog is global for now, but could be filtered too
        context['blogs'] = ArticleBlog.objects.all().order_by('-date_publication')[:3]
        return context

class MallTableListView(ListView):
    model = Mall
    template_name = 'mall/mall_table_list.html'
    context_object_name = 'malls'
# ================ End Start Home views =======================

# ================ Start Mall views ==========================
class MallView(TemplateView):
    """Specific Mall Homepage — shows featured stores/events for a mall."""
    template_name = 'mall/mall.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mall_slug = self.kwargs.get('slug')
        mall = get_object_or_404(Mall, slug=mall_slug)
        context['mall'] = mall
        context['shops_featured'] = mall.shops.all() #filter(is_featured=True)[:6]
        context['future_events'] = mall.events.all() #.order_by('date')[:3]
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
    template_name = 'mall/mall_form.html'
    success_url = reverse_lazy('home')

class MallUpdateView(UpdateView):
    model = Mall
    form_class = MallForm
    template_name = 'mall/mall_form.html'
    success_url = reverse_lazy('home')

class MallDeleteView(DeleteView):
    model = Mall
    template_name = 'mall/mall_confirm_delete.html'
    success_url = reverse_lazy('home')

# class MallDetailView(DetailView):
#     model = Mall
#     template_name = 'mall/mall_detail.html'
#     context_object_name = 'mall'

# ================ End Mall views ==========================

# ================ Start Promotion views ==========================
class PromotionListView(ListView):
    model = Promotion
    template_name = 'mall/promotion_list.html'
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

class ShopCreateView(CreateView):
    model = Shop
    form_class = ShopForm
    template_name = 'mall/shop_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.mall = get_object_or_404(Mall, slug=self.kwargs.get('slug'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.mall = self.mall
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mall'] = self.mall
        return context

    def get_success_url(self):
        return reverse('shops_by_mall', kwargs={'slug': self.mall.slug})

class ShopListView(ListView):
    model = Shop
    template_name = 'mall/shop_list.html'
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
    template_name = 'mall/shop_detail.html'
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
    template_name = 'mall/event_list.html'
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
    template_name = 'mall/event_detail.html'
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
    template_name = 'mall/blog_list.html'
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
    template_name = 'mall/blog_detail.html'
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

class ContactMessageCreateView(CreateView):
    model = ContactMessage
    form_class = ContactForm
    template_name = 'mall/contact_message.html'

    def dispatch(self, request, *args, **kwargs):
        self.mall = get_object_or_404(Mall, slug=self.kwargs.get('slug'))  # ✅
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

class ContactMessageListView(ListView):
    model = ContactMessage
    template_name = 'mall/contacts_messages_list.html'
    context_object_name = 'contacts'
    ordering = ['-created_at']

    def get_queryset(self):
        self.mall_slug = self.kwargs.get('slug')  # ✅ التصحيح هنا
        self.mall = None

        if self.mall_slug:
            self.mall = get_object_or_404(Mall, slug=self.mall_slug)
            return ContactMessage.objects.filter(mall=self.mall).order_by('-created_at')

        return ContactMessage.objects.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mall'] = self.mall #get_object_or_404(Mall, slug=self.kwargs['mall_slug'])
        return context

class ContactMessageDetailView(DetailView):
    model = ContactMessage
    template_name = 'mall/contact_message_detail.html'
    context_object_name = 'contact'

    def get_object(self):
        return get_object_or_404(ContactMessage, id=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mall'] = self.object.mall
        return context

class ContactMessageDeleteView(DeleteView):
    model = ContactMessage
    template_name = 'mall/contact_message_delete.html'
    context_object_name = 'contact'

    def get_object(self):
        return get_object_or_404(ContactMessage, id=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mall'] = self.object.mall
        return context  

    def get_success_url(self):
        return reverse('contacts_messages_by_mall', 
                      kwargs={
                            'slug': self.object.mall.slug
                        })

# ================ End Contact views ==========================
# ================ Start Product views ==========================

class ProductListView(ListView):
    model = Product
    template_name = 'mall/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        self.mall_slug = self.kwargs.get('slug')
        self.category_slug = self.request.GET.get('category')
        self.query = self.request.GET.get('q', '').strip()

        queryset = Product.objects.select_related('shop', 'shop__mall', 'category')

        if self.mall_slug:
            self.mall = get_object_or_404(Mall, slug=self.mall_slug)
            queryset = queryset.filter(shop__mall=self.mall)
        else:
            self.mall = None

        if self.category_slug:
            queryset = queryset.filter(category__slug=self.category_slug)

        if self.query:
            queryset = queryset.filter(
                Q(name__icontains=self.query) |
                Q(shop__name__icontains=self.query)
            )

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import ProductCategory
        context.update({
            'mall': self.mall,
            'categories': ProductCategory.objects.all(),
            'selected_category': self.category_slug,
            'search_query': self.query,
        })
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'mall/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_products'] = Product.objects.filter(category=self.object.category).exclude(id=self.object.id)[:4]
        return context
class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'mall/product_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.shop = get_object_or_404(Shop, slug=self.kwargs.get('shop_slug'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.shop = self.shop
        response = super().form_valid(form)
        self.save_images()
        return response

    def save_images(self):
        images = self.request.FILES.getlist('images')
        main_index = int(self.request.POST.get('main_index', 0))

        if not images:
            return

        if main_index >= len(images):
            main_index = 0

        for i, image in enumerate(images):
            ProductImages.objects.create(
                product=self.object,
                image=image,
                is_main=(i == main_index)
            )

    def get_success_url(self):
        return reverse(
            'shop_detail',
            kwargs={
                'mall_slug': self.shop.mall.slug,
                'slug': self.shop.slug
            }
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        return context


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'mall/product_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        self.save_images()
        return response

    def save_images(self):
        images = self.request.FILES.getlist('images')
        main_index = int(self.request.POST.get('main_index', 0))

        if not images:
            return

        if main_index >= len(images):
            main_index = 0

        for i, image in enumerate(images):
            ProductImages.objects.create(
                product=self.object,
                image=image,
                is_main=(i == main_index)
            )


    def get_success_url(self):
        return self.object.get_absolute_url()   

class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'mall/product_confirm_delete.html'

    def get_success_url(self):
        return reverse('shop_detail', kwargs={'mall_slug': self.object.shop.mall.slug, 'slug': self.object.shop.slug})

# ================ End Product views ==========================

from django.views.decorators.http import require_POST

@login_required
@require_POST
def product_image_delete(request, id):
    image = get_object_or_404(ProductImages, id=id)
    product = image.product
    image.delete()
    return redirect(product.get_absolute_url())

@login_required
@require_POST
def product_image_set_main(request, id):
    image = get_object_or_404(ProductImages, id=id)
    product = image.product
    
    # Reset all images for this product to not be main
    product.images.update(is_main=False)
    
    # Set the selected image as main
    image.is_main = True
    image.save()
    
    return redirect(product.get_absolute_url())

