
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
    path('user-add/', views.add_user, name='user_add'),
    path('user-update/<str:username>/',views.user_update, name="user_update"),
    path('user-delete/<str:username>/', views.UserDeleteView.as_view(), name='user_delete'),
    path('users/manage/', views.UsersManageView.as_view(), name='users_manage'),
    

    path('user-toggle/<int:user_id>/', views.ToggleUserStatusView.as_view(), name='user_toggle'),


    #--------------------- / Auth -------------------------
  
    # Dashboards
    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('mall/<slug:slug>/dashboard/', views.MallDashboardView.as_view(), name='mall_dashboard'),
    path('shop/<slug:slug>/dashboard/', views.ShopDashboardView.as_view(), name='shop_dashboard'),
    
   
    # Malls 
    path('mall/add/', views.MallCreateView.as_view(), name='mall_create'),
    path('mall/<slug:slug>/', views.MallView.as_view(), name='mall'),
    path('malls/', views.MallListView.as_view(), name='mall_list'),
    path('malls/manage/', views.MallsManageView.as_view(), name='malls_manage'),
    path('mall/<slug:slug>/edit/', views.MallUpdateView.as_view(), name='mall_update'),
    path('mall/<slug:slug>/delete/', views.MallDeleteView.as_view(), name='mall_delete'),
    
    path('mall-toggle/<int:mall_id>/', views.ToggleMallStatusView.as_view(), name='mall_toggle'),

    # Shops
    path('mall/<slug:slug>/shop/add/', views.ShopCreateView.as_view(), name='shop_create'),
    path('mall/<slug:mall_slug>/shop/<slug:shop_slug>/edit/', views.ShopUpdateView.as_view(), name='shop_update'),
    path('mall/<slug:mall_slug>/shop/<slug:shop_slug>/delete/', views.ShopDeleteView.as_view(), name='shop_delete'),
    path('mall/<slug:mall_slug>/shop/<slug:slug>/', views.ShopDetailView.as_view(), name='shop'),
    path('shops/', views.ShopListView.as_view(), name='shops_all'),
    path('shops/manage/', views.ShopsManageView.as_view(), name='shops_manage'),
    path('mall/<slug:slug>/shops/', views.ShopListView.as_view(), name='shops_by_mall'),
    
    # Promotions
    path('promotions/', views.PromotionListView.as_view(), name='promotions_all'),
    path('mall/<slug:slug>/promotions/', views.PromotionListView.as_view(), name='promotions_by_mall'),
    path('mall/<slug:mall_slug>/shop/<slug:shop_slug>/promotion/add/', views.PromotionCreateView.as_view(), name='promotion_create'),
    path('mall/<slug:mall_slug>/shop/<slug:shop_slug>/promotion/<int:pk>/edit/', views.PromotionUpdateView.as_view(), name='promotion_update'),
    path('mall/<slug:mall_slug>/shop/<slug:shop_slug>/promotion/<int:pk>/delete/', views.PromotionDeleteView.as_view(), name='promotion_delete'),

    # Événements
    path('events/', views.EventListView.as_view(), name='events_all'),
    path('mall/<slug:slug>/events/', views.EventListView.as_view(), name='events_by_mall'),

    path('mall/<slug:mall_slug>/event/add/', views.EventCreateView.as_view(), name='event_create'),
    path('mall/<slug:mall_slug>/event/<slug:slug>/', views.EventDetailView.as_view(), name='event_detail'),
    path('mall/<slug:mall_slug>/event/<slug:slug>/edit/', views.EventUpdateView.as_view(), name='event_update'),
    path('mall/<slug:mall_slug>/event/<slug:slug>/delete/', views.EventDeleteView.as_view(), name='event_delete'),    
    # Blog
    path('blogs/', views.ArticleBlogListView.as_view(), name='blogs_all'),
    path('mall/<slug:slug>/blogs/', views.ArticleBlogListView.as_view(), name='blogs_by_mall'),
    path('mall/<slug:mall_slug>/blog/<slug:slug>/', views.ArticleBlogDetailView.as_view(), name='blog_detail'),

    # Contact messages
    path('contact/', views.ContactMessageCreateView.as_view(), name='contact_message_create'),
    path('mall/<slug:slug>/contact/', views.ContactMessageCreateView.as_view(), name='contact_message_create_by_mall'),


    path('mall/<slug:slug>/contacts/', views.ContactMessageListView.as_view(), name='contacts_messages_by_mall'),
    path('contacts/', views.ContactMessageListView.as_view(), name='contacts_messages_all'),
    path('mall/<slug:mall_slug>/contact/<int:id>/', views.ContactMessageDetailView.as_view(), name='contact_message_detail'),
    path('mall/<slug:mall_slug>/contact/<int:id>/delete/', views.ContactMessageDeleteView.as_view(), name='contact_message_delete'),

    # Category
    # path('category/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('category/ajax/add/', views.category_ajax_add, name='category_ajax_add'),


    # Product
    path('mall/<slug:mall_slug>/shop/<slug:shop_slug>/product/add/', views.ProductCreateView.as_view(), name='product_create'),
    path('mall/<slug:mall_slug>/shop/<slug:shop_slug>/product/<slug:product_slug>/', views.ProductDetailView.as_view(), name='product'),
    path('mall/<slug:mall_slug>/shop/<slug:shop_slug>/product/<slug:product_slug>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('mall/<slug:mall_slug>/shop/<slug:shop_slug>/product/<slug:product_slug>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('mall/<slug:slug>/products/', views.ProductListView.as_view(), name='products_by_mall'),
    path('products/', views.ProductListView.as_view(), name='products_all'),

    # Product Images (AJAX / Actions)
    path('product-image/<int:id>/delete/', views.product_image_delete, name='product_image_delete'),
    path('product-image/<int:id>/set-main/', views.product_image_set_main, name='product_image_set_main'),


    # Wishlist
    path('wishlist/', views.wishlist_list, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.wishlist_toggle, name='wishlist_toggle'),
    path('wishlist/to-cart/<int:product_id>/', views.wishlist_to_cart, name='wishlist_to_cart'),

    # Cart & Checkout
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:item_id>/', views.cart_update, name='cart_update'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/success/', views.checkout_success, name='checkout_success'),
    
    # Order History
    path('history/', views.order_history, name='order_history'),
    
    # path('order/create/', views.order_create, name='order_create'),

    path('order/detail/<int:pk>/', views.order_detail, name='order_detail'),
    path('order/update/<int:pk>/', views.order_update, name='order_update'),
    path('order/delete/<int:pk>/', views.order_delete, name='order_delete'),

    path('order-item/<int:pk>/status/<str:status>/', views.order_item_status, name='order_item_status'),
    path('order/<int:pk>/status/<str:status>/', views.order_status, name='order_status'),

    path('orders/', views.order_list, name='order_list_all'),
    path('orders/<int:userid>', views.order_list, name='order_list_user'),
    path('mall/<slug:slug>/delivery-office/', views.order_list_by_mall, name='order_list_by_mall'),

    path('orders/items/', views.orders_items_list, name='orders_items_list_all'),
    path('orders/items/<slug:shop_slug>/', views.orders_items_list, name='orders_items_list_shop'),





]  

