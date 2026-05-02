from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.db.models import Q,Sum
from .models import Profile, Mall,Shop, Event, Promotion, ArticleBlog, ContactMessage, Product, ProductImages, Order,OrderHistory, OrderItem, OrderItemHistory, Wishlist
from .forms import NewUserCreationForm, UserUpdateForm, ProfileUpdateForm,MallForm, ShopForm, ContactForm, ProductForm, OrderUpdateForm, OrderItemFormSet
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.utils import timezone

# from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User

import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from django.views import View


# ============================================================================
# AUTH VIEWS
# ============================================================================

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


@login_required # create_user
@user_passes_test(lambda u: u.is_superuser)
def add_user(request):
    if request.method == 'POST':
        form = NewUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('users_manage')
    else:
        form = NewUserCreationForm()
    
    context = {
            'form': form
    }
    return render(request, 'registration/user_add.html', context)


@login_required # user_update
def user_update(request, username):
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
    return render(request, 'registration/user_update.html', context)

class UserDeleteView(DeleteView):
    model = User
    template_name = 'registration/user_confirm_delete.html'
    context_object_name = 'user'
    success_url = reverse_lazy('users_manage')

    slug_field = 'username'
    slug_url_kwarg = 'username'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('users_manage')
        return super().dispatch(request, *args, **kwargs)
    
    # def get_object(self, queryset=None):
    #     obj = super().get_object()
    #     if obj == self.request.user:
    #         raise PermissionDenied("You cannot delete yourself")
    #     return obj


class ToggleUserStatusView(View):
    def post(self, request, user_id):
        if not request.user.is_superuser:
            return redirect('users_manage')

        user = get_object_or_404(User, id=user_id)

        # تبديل الحالة
        user.is_active = not user.is_active
        user.save()

        return redirect('users_manage')


# ================ End Auth views ==========================


# ============================================================================
# HOME VIEWS
# ============================================================================

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

class AdminDashboardView(TemplateView):
    template_name = 'mall/admin_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, "Accès restreint aux administrateurs.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['malls_count'] = Mall.objects.count()
        context['shops_count'] = Shop.objects.count()
        context['users_count'] = User.objects.count()
        context['orders_count'] = Order.objects.count()
        context['recent_orders'] = Order.objects.select_related('user').all()[:5]
        context['recent_users'] = User.objects.order_by('-date_joined')[:5]
        return context

class UsersManageView(ListView):
    model = User
    template_name = 'registration/users_manage.html'
    context_object_name = 'users'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = User.objects.select_related('profile').all().order_by('-date_joined')
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(username__icontains=q) |
                Q(email__icontains=q) |
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q)
            )
        return queryset


class ShopsManageView(ListView):
    model = Shop
    template_name = 'mall/shops_manage.html'
    context_object_name = 'shops'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = Shop.objects.select_related('mall', 'owner').all().order_by('name')
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) |
                Q(mall__name__icontains=q) |
                Q(owner__username__icontains=q)
            )
        return queryset

class MallsManageView(ListView):
    model = Mall
    template_name = 'mall/malls_manage.html'
    context_object_name = 'malls'

class MallDashboardView(TemplateView):
    template_name = 'mall/mall_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        self.mall = get_object_or_404(Mall, slug=self.kwargs.get('slug'))
        # Check permissions: Superuser or Assigned Manager
        if not request.user.is_superuser and self.mall.manager != request.user:
            messages.error(request, "Vous n'avez pas les droits pour gérer ce centre.")
            return redirect('mall', self.mall.slug)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mall'] = self.mall
        context['shops_count'] = self.mall.shops.count()
        context['products_count'] = Product.objects.filter(shop__mall=self.mall).count()
        context['orders_count'] = Order.objects.filter(items__product__shop__mall=self.mall).distinct().count()
        context['recent_shops'] = self.mall.shops.all().order_by('-id')[:5]
        context['recent_orders'] = Order.objects.filter(items__product__shop__mall=self.mall).distinct().order_by('-created_at')[:5]
        return context

class ShopDashboardView(TemplateView):
    template_name = 'mall/shop_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        self.shop = get_object_or_404(Shop, slug=self.kwargs.get('slug'))
        # Check permissions: Superuser, Mall Manager, or Shop Owner
        if not request.user.is_superuser and self.shop.owner != request.user and self.shop.mall.manager != request.user:
            messages.error(request, "Vous n'avez pas les droits pour gérer cette boutique.")
            return redirect('shop', self.shop.mall.slug, self.shop.slug)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        context['products_count'] = self.shop.products.count()
        context['promotions_count'] = self.shop.promotions.count()
        context['orders_count'] = Order.objects.filter(items__product__shop=self.shop).distinct().count()
        context['recent_products'] = self.shop.products.all().order_by('-created_at')[:5]
        context['recent_orders'] = Order.objects.filter(items__product__shop=self.shop).distinct().order_by('-created_at')[:5]
        return context

class MallListView(ListView):

    model = Mall
    template_name = 'mall/mall_list.html'
    context_object_name = 'malls'

# ================ End Home views ==========================


# ============================================================================
# MALL VIEWS
# ============================================================================

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



class ToggleMallStatusView(View):
    def post(self, request, mall_id):
        if not request.mall.is_actif:
            return redirect('malls_manage')

        mall = get_object_or_404(Mall, id=mall_id)

        # تبديل الحالة
        mall.is_actif = not mall.is_actif
        mall.save()

        return redirect('malls_manage')



# ================ End Mall views ==========================

# ============================================================================
# PROMOTION VIEWS
# ============================================================================

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
# ================ End P    romotion views ==========================

# ============================================================================
# SHOP VIEWS
# ============================================================================

class ShopCreateView(CreateView):
    model = Shop
    form_class = ShopForm
    template_name = 'mall/shop_form.html'

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        self.mall = None
        if slug and slug != 'default':
            self.mall = get_object_or_404(Mall, slug=slug)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if self.mall:
            form.instance.mall = self.mall
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mall'] = self.mall
        return context

    def get_success_url(self):
        if self.mall:
            return reverse('shops_by_mall', kwargs={'slug': self.mall.slug})
        return reverse('mall_dashboard')

class ShopUpdateView(UpdateView):
    model = Shop
    form_class = ShopForm
    template_name = 'mall/shop_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.mall = get_object_or_404(Mall, slug=self.kwargs['mall_slug'])
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(
            Shop,
            slug=self.kwargs['shop_slug'],
            mall=self.mall
        )

    def form_valid(self, form):
        form.instance.mall = self.mall
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mall'] = self.mall
        return context

    def get_success_url(self):
        return reverse('shops_by_mall', kwargs={'slug': self.mall.slug})

class ShopDeleteView(DeleteView):
    model = Shop
    template_name = 'mall/shop_confirm_delete.html'
    success_url = reverse_lazy('shops_manage')

    def get_object(self, queryset=None):
        self.mall = get_object_or_404(Mall, slug=self.kwargs['mall_slug'])
        return get_object_or_404(
            Shop,
            slug=self.kwargs['shop_slug'],
            mall=self.mall
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mall'] = self.mall
        return context

    def get_success_url(self):
        return reverse('shops_manage', kwargs={'slug': self.mall.slug})

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
    template_name = 'mall/Shop.html'
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
        
        user_wishlist_ids = []
        if self.request.user.is_authenticated:
            wishlist, _ = Wishlist.objects.get_or_create(user=self.request.user)
            user_wishlist_ids = wishlist.products.values_list('id', flat=True)

        context.update({
            'mall': mall,  # 👈 الآن مضمون دائماً
            'related_shops': related_shops,
            'user_wishlist_ids': user_wishlist_ids,
        })

        return context
# ================   End Shop views ==========================


# ============================================================================
# EVENT VIEWS
# ============================================================================

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
# ================ End Event views ==========================


# ============================================================================
# BLOG VIEWS
# ============================================================================

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


# ============================================================================
# CONTACT VIEWS
# ============================================================================

class ContactMessageCreateView(CreateView):
    model = ContactMessage
    form_class = ContactForm
    template_name = 'mall/contact_message.html'

    def dispatch(self, request, *args, **kwargs):
        # 👇 نخليها optional
        self.mall = None
        mall_slug = self.kwargs.get('slug')

        if mall_slug:
            self.mall = get_object_or_404(Mall, slug=mall_slug)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # ✅ اربط بالمول إذا موجود
        if self.mall:
            form.instance.mall = self.mall

        form.save()

        messages.success(self.request, "Message envoyé avec succès")

        # ✅ redirect ذكي
        if self.mall:
            return redirect('mall', self.mall.slug)
        return redirect('home')  # 👈 أو أي صفحة عامة

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mall'] = self.mall  # ممكن تكون None
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

# ============================================================================
# PRODUCT VIEWS
# ============================================================================

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
        from .models import ProductCategory, Wishlist
        
        user_wishlist_ids = []
        if self.request.user.is_authenticated:
            wishlist, _ = Wishlist.objects.get_or_create(user=self.request.user)
            user_wishlist_ids = wishlist.products.values_list('id', flat=True)

        context.update({
            'mall': self.mall,
            'categories': ProductCategory.objects.all(),
            'selected_category': self.category_slug,
            'search_query': self.query,
            'user_wishlist_ids': user_wishlist_ids,
        })
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'mall/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_products'] = Product.objects.filter(category=self.object.category).exclude(id=self.object.id)[:4]
        
        is_in_wishlist = False
        if self.request.user.is_authenticated:
            from .models import Wishlist
            wishlist, _ = Wishlist.objects.get_or_create(user=self.request.user)
            is_in_wishlist = self.object in wishlist.products.all()
            
        context['is_in_wishlist'] = is_in_wishlist
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
            'shop',
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
        return reverse('shop', kwargs={'mall_slug': self.object.shop.mall.slug, 'slug': self.object.shop.slug})

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

# ================ End Product views ==========================

# ============================================================================
# WISHLIST VIEWS
# ============================================================================

@login_required
@require_POST
def wishlist_toggle(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    if wishlist.products.filter(id=product.id).exists():
        wishlist.products.remove(product)
        status = 'removed'
    else:
        wishlist.products.add(product)
        status = 'added'

    # ⭐ مهم جداً: نحسب العدد
    wishlist_count = wishlist.products.count()

    return JsonResponse({
        'status': status,
        'wishlist_count': wishlist_count
    })


    

@login_required
def wishlist_list(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    products = wishlist.products.all()
    
    context = {
        'products': products,
    }
    return render(request, 'mall/wishlist.html', context)

@login_required
@require_POST
def wishlist_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Remove from wishlist
    wishlist = getattr(request.user, 'wishlist', None)
    if wishlist and product in wishlist.products.all():
        wishlist.products.remove(product)
        
    # Add to cart
    order, created = Order.objects.get_or_create(user=request.user, status='pending')
    order_item, item_created = OrderItem.objects.get_or_create(
        order=order, 
        product=product,
        defaults={'quantity': 1, 'price': product.price}
    )
    if not item_created:
        order_item.quantity += 1
        order_item.save()
        
    order.update_total_price()
    return JsonResponse({'status': 'success'})

# ================ End Wishlist views ==========================

# ============================================================================
# CART & CHECKOUT VIEWS
# ============================================================================

@login_required
def cart_view(request):
    order, created = Order.objects.get_or_create(user=request.user, status='pending')
    order.update_total_price() # ensure total is fresh
    context = {
        'order': order,
        'items': order.items.all().order_by('id')
    }
    return render(request, 'mall/cart.html', context)

@login_required
@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    order, created = Order.objects.get_or_create(user=request.user, status='pending')
    
    order_item, item_created = OrderItem.objects.get_or_create(
        order=order, 
        product=product,
        defaults={'quantity': 1, 'price': product.price}
    )
    
    if not item_created:
        order_item.quantity += 1
        order_item.save()
        
    order.update_total_price()
    return JsonResponse({'status': 'success', 'cart_count': sum(item.quantity for item in order.items.all())})

@login_required
@require_POST
def cart_remove(request, item_id):
    order_item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__status='pending')
    order = order_item.order
    order_item.delete()
    order.update_total_price()
    return JsonResponse({'status': 'success'})

@login_required
@require_POST
def cart_update(request, item_id):
    order_item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__status='pending')
    
    try:
        data = json.loads(request.body)
        action = data.get('action')
    except:
        action = None
        
    if action == 'increment':
        order_item.quantity += 1
    elif action == 'decrement':
        order_item.quantity -= 1
        
    if order_item.quantity <= 0:
        order_item.delete()
    else:
        order_item.save()
        
    order_item.order.update_total_price()
    return JsonResponse({'status': 'success'})

@login_required
def checkout(request):
    order = get_object_or_404(Order, user=request.user, status='pending')
    if order.items.count() == 0:
        messages.warning(request, "Your cart is empty.")
        return redirect('cart')
        
    if request.method == 'POST':
        order.status = 'delivered' # As requested, treating this as checkout completion
        order.save()
        messages.success(request, "Your order has been placed successfully!")
        return redirect('checkout_success')
        
    return render(request, 'mall/checkout.html', {'order': order})

@login_required
def checkout_success(request):
    return render(request, 'mall/checkout_success.html')

# ================ End Cart & Checkout views ==========================

# ============================================================================
# ORDER HISTORY VIEWS
# ============================================================================

@login_required # order_history
def order_history(request):     
    orders = Order.objects.filter(user=request.user, status='delivered').order_by('-id')
    return render(request, 'mall/order_history.html', {'orders': orders})

@login_required # order_list all / by user
def order_list(request, userid=None):

    # 🔒 حماية
    if not request.user.is_superuser:
        userid = request.user.id

    orders = Order.objects.filter(user_id=userid) if userid else Order.objects.all()

    orders = orders.select_related('user') \
        .prefetch_related('items', 'items__product', 'history') \
        .order_by('-created_at')

    search = request.GET.get('search', '')

    if search:
        if search.isdigit():
            orders = orders.filter(
                Q(id=int(search)) |
                Q(user__username__icontains=search) |
                Q(status__icontains=search)
            )
        else:
            orders = orders.filter(
                Q(user__username__icontains=search) |
                Q(status__icontains=search)
            )

    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    order_pages = paginator.get_page(page_number)

    return render(request, 'mall/order_list.html', {
        'search': search,
        'orders': order_pages,
        'status_choices': Order.STATUS_CHOICES,
        'order_item_status_choices': OrderItem.STATUS_CHOICES,
    })

@login_required # order_list_by_mall
def order_list_by_mall(request, slug):
    mall = get_object_or_404(Mall, slug=slug)
    # Get orders that have items from this mall
    orders = Order.objects.filter(items__product__shop__mall=mall).distinct().select_related('user') \
                  .prefetch_related('items__product__shop__mall', 'history').order_by('-created_at')

    search = request.GET.get('search', '')
    if search:
        orders = orders.filter(
            Q(id__icontains=search) |
            Q(status__icontains=search) |
            Q(user__username__icontains=search)
        )
     
    # pagination
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    order_pages = paginator.get_page(page_number)

    return render(request, 'mall/order_list.html', {
        'mall': mall,
        'search': search,
        'orders': order_pages,
        'status_choices': Order.STATUS_CHOICES,
        'order_item_status_choices': OrderItem.STATUS_CHOICES,
    })

@login_required # orders items list (all / shop)
def orders_items_list(request, shop_slug = None): 

    if shop_slug:
        shop  = get_object_or_404(Shop, slug=shop_slug)
        items = OrderItem.objects.filter(product__shop=shop).select_related('order', 'product').order_by('-order_id')
    else:
        shop  = "Tous les Magasins" #None
        items = OrderItem.objects.all().select_related('order', 'product', 'product__shop').order_by('-order_id')

    # ---------- pagination
    paginator = Paginator(items, 15)
    page_number = request.GET.get('page')
    item_pages = paginator.get_page(page_number)
    
    return render(request, 'mall/order_items_list.html', {
        'shop' : shop,
        'items': item_pages,
        'item_pages': item_pages,
        'status_choices': OrderItem.STATUS_CHOICES,
    })

@login_required # order detail 
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'mall/order_detail.html', {'order': order})

@login_required # order update 
def order_update(request, pk):
    order = get_object_or_404(Order, pk=pk)

    # Permission check
    if order.user != request.user and not request.user.is_superuser:
        messages.error(request, "You cannot edit this order")
        return redirect('order_list_all')

    old_status = order.status

    if request.method == 'POST':
        form = OrderUpdateForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order)

        if form.is_valid() and formset.is_valid():
            order = form.save(commit=True)

            # Save formset: this handles both updates and marked-for-deletion items
            instances = formset.save(commit=False)
            for obj in instances:
                obj.save()
            for obj in formset.deleted_objects:
                obj.delete()

            # Refresh from DB so update_total_price sees the current items
            order.refresh_from_db()

            # Recompute totals and derive order status from item statuses
            order.update_total_price()
            order.update_status_from_items()

            # Refresh again after status may have changed
            order.refresh_from_db()

            # Save history if status changed
            if order.status != old_status:
                OrderHistory.objects.create(
                    order=order,
                    old_status=old_status,
                    new_status=order.status,
                    changed_by=request.user if request.user.is_authenticated else None
                )

            messages.success(request, "Commande mise à jour avec succès.")
            return redirect('order_detail', pk=order.pk)
    else:
        form = OrderUpdateForm(instance=order)
        formset = OrderItemFormSet(instance=order)

    return render(request, 'mall/order_update.html', {
        'form': form,
        'formset': formset,
        'order': order
    })

@login_required # order delete 
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.user != request.user and not request.user.is_superuser:
        messages.error(request, "You cannot delete this order")
        return redirect('order_list')

    if request.method == 'POST':
        order.delete()
        messages.success(request, "Order deleted")
        return redirect('order_list_user', userid=order.user.id)

    return render(request, 'mall/order_confirm_delete.html', {'order': order})

@login_required # order item status
def order_item_status(request, pk, status):
    item = get_object_or_404(OrderItem, pk=pk)

    # تحقق أن الحالة صالحة
    valid_statuses = [s[0] for s in OrderItem.STATUS_CHOICES]
    if status in valid_statuses:
        old = item.status
        item.status = status
        item.save(update_fields=['status'])

        # حفظ التاريخ
        OrderItemHistory.objects.create(
            order_item=item,
            old_status=old,
            new_status=status,
            changed_by=request.user if request.user.is_authenticated else None
        )

        # تحديث حالة الطلب
        item.order.update_status_from_items()

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)

    if request.user.is_superuser:
        return redirect('orders_items_list_all')   # مهم لإعادة تحميل الصفحة
    return redirect('orders_items_list_shop', item.product.shop.slug) # مهم لإعادة تحميل الصفحة    

@login_required # order status
def order_status(request, pk, status):
    order = get_object_or_404(Order, pk=pk)

    valid_statuses = [s[0] for s in Order.STATUS_CHOICES]

    if status in valid_statuses:
        old = order.status
        order.status = status
        order.save(update_fields=['status'])

        OrderHistory.objects.create(
            order=order,
            old_status=old,
            new_status=status,
            changed_by=request.user if request.user.is_authenticated else None
        )
        
        order.propagate_status_to_items(user=request.user if request.user.is_authenticated else None)

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)

    return redirect('order_list_all')


# ================ End Order History views ==========================