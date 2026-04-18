
from django.conf import settings
from django.conf.urls.static import static

from django.urls import path, include
from . import views

urlpatterns = [
    # Portal — choose your mall (root page)
    path('', views.HomeView.as_view(), name='home'),




    # ============================================================================
    # AUTHENTICATION & ACCOUNT MANAGEMENT
    # ============================================================================
  
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', views.signup, name='signup'),
    path('update-profile/<str:username>/',views.update_profile, name="update_profile"),
    #--------------------- / Auth -------------------------
  





    # Mall Management BBMalls
    path('malls/', views.MallTableListView.as_view(), name='mall_table_list'),
    path('malls/add/', views.MallCreateView.as_view(), name='mall_create'),
    path('malls/<slug:slug>/edit/', views.MallUpdateView.as_view(), name='mall_update'),
    path('malls/<slug:slug>/delete/', views.MallDeleteView.as_view(), name='mall_delete'),
    
    # Mall
    path('mall/<slug:slug>/', views.MallView.as_view(), name='mall'),

    # Shops
    path('mall/<slug:slug>/shop/add/', views.ShopCreateView.as_view(), name='shop_create'),
    path('mall/<slug:mall_slug>/shop/<slug:slug>/', views.ShopDetailView.as_view(), name='shop_detail'),
    path('shops/', views.ShopListView.as_view(), name='shops_all'),
    path('mall/<slug:slug>/shops/', views.ShopListView.as_view(), name='shops_by_mall'),
    
    # Promotions
    path('promotions/', views.PromotionListView.as_view(), name='promotions_all'),
    path('mall/<slug:slug>/promotions/', views.PromotionListView.as_view(), name='promotions_by_mall'),

    # Événements
    path('events/', views.EventListView.as_view(), name='events_all'),
    path('mall/<slug:slug>/events/', views.EventListView.as_view(), name='events_by_mall'),
    # path('evenement/<slug:slug>/', views.EvenementDetailView.as_view(), name='evenement_detail'),
    path('mall/<slug:mall_slug>/event/<slug:slug>/', views.EventDetailView.as_view(), name='event_detail'),
       
    # Blog
    path('blogs/', views.ArticleBlogListView.as_view(), name='blogs_all'),
    path('mall/<slug:slug>/blogs/', views.ArticleBlogListView.as_view(), name='blogs_by_mall'),
    path('mall/<slug:mall_slug>/blog/<slug:slug>/', views.ArticleBlogDetailView.as_view(), name='blog_detail'),

    # Contact messages
    path('mall/<slug:slug>/contact/', views.ContactMessageCreateView.as_view(), name='contact_message_create'),
   
    path('mall/<slug:slug>/contacts/', views.ContactMessageListView.as_view(), name='contacts_messages_by_mall'),
    path('contacts/', views.ContactMessageListView.as_view(), name='contacts_messages_all'),
    path('mall/<slug:mall_slug>/contact/<int:id>/', views.ContactMessageDetailView.as_view(), name='contact_message_detail'),
    path('mall/<slug:mall_slug>/contact/<int:id>/delete/', views.ContactMessageDeleteView.as_view(), name='contact_message_delete'),

    # Product
    path('mall/<slug:mall_slug>/shop/<slug:shop_slug>/product/add/', views.ProductCreateView.as_view(), name='product_create'),
    path('mall/<slug:mall_slug>/shop/<slug:shop_slug>/product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('mall/<slug:mall_slug>/shop/<slug:shop_slug>/product/<slug:slug>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('mall/<slug:mall_slug>/shop/<slug:shop_slug>/product/<slug:slug>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('mall/<slug:slug>/products/', views.ProductListView.as_view(), name='products_by_mall'),
    path('products/', views.ProductListView.as_view(), name='products_all'),

    # Product Images (AJAX / Actions)
    path('product-image/<int:id>/delete/', views.product_image_delete, name='product_image_delete'),
    path('product-image/<int:id>/set-main/', views.product_image_set_main, name='product_image_set_main'),
]
