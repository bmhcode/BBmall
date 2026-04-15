from django.urls import path
from . import views

urlpatterns = [
    # Portal — choose your mall (root page)
    path('', views.HomeView.as_view(), name='home'),
    
    # Mall Management BBMalls
    path('malls/', views.MallTableListView.as_view(), name='mall_table_list'),
    path('malls/add/', views.MallCreateView.as_view(), name='mall_create'),
    path('malls/<slug:slug>/edit/', views.MallUpdateView.as_view(), name='mall_update'),
    path('malls/<slug:slug>/delete/', views.MallDeleteView.as_view(), name='mall_delete'),
    
    # Mall
    path('mall/<slug:slug>/', views.MallView.as_view(), name='mall'),

    # Magasins
    path('magasins/', views.MagasinListView.as_view(), name='magasins_all'),
    path('mall/<slug:slug>/magasins/', views.MagasinListView.as_view(), name='magasins_by_mall'),
    path('mall/<slug:mall_slug>/magasin/<slug:slug>/', views.MagasinDetailView.as_view(), name='magasin_detail'),
    
    # Promotions
    path('promotions/', views.PromotionListView.as_view(), name='promotions_all'),
    path('mall/<slug:slug>/promotions/', views.PromotionListView.as_view(), name='promotions_by_mall'),

    # Événements
    path('evenements/', views.EvenementListView.as_view(), name='evenements_all'),
    path('mall/<slug:slug>/evenements/', views.EvenementListView.as_view(), name='evenements_by_mall'),
    # path('evenement/<slug:slug>/', views.EvenementDetailView.as_view(), name='evenement_detail'),
    path('mall/<slug:mall_slug>/evenement/<slug:slug>/', views.EvenementDetailView.as_view(), name='evenement_detail'),
       
    # Blog
    path('blogs/', views.ArticleBlogListView.as_view(), name='blogs_all'),
    path('mall/<slug:slug>/blogs/', views.ArticleBlogListView.as_view(), name='blogs_by_mall'),
    path('mall/<slug:mall_slug>/blog/<slug:slug>/', views.ArticleBlogDetailView.as_view(), name='blog_detail'),
    




    # Contact
    path('mall/<slug:mall_slug>/contact/', views.ContactCreateView.as_view(), name='contact_create'),
    path('mall/<slug:mall_slug>/contacts/', views.ContactListView.as_view(), name='contacts_by_mall'),
    path('contacts/', views.ContactListView.as_view(), name='contacts_all'),
    path('mall/<slug:mall_slug>/contact/<int:id>/', views.ContactDetailView.as_view(), name='contact_detail'),
    path('mall/<slug:mall_slug>/contact/<int:id>/delete/', views.ContactDeleteView.as_view(), name='contact_delete'),




    # Individual mall homepage (the "Entered" mall experience)
    # path('magasins/', views.MagasinListView.as_view(), name='magasin_list'),
    # path('magasin/<slug:slug>/', views.MagasinDetailView.as_view(), name='magasin_detail'),
    # path('evenements/', views.EvenementListView.as_view(), name='evenement_list'),
    # path('evenements/<slug:slug>/', views.EvenementDetailView.as_view(), name='evenement_detail'),
    # path('promotions/', views.PromotionListView.as_view(), name='promotion_list'),
    # path('blog/', views.ArticleBlogListView.as_view(), name='blog_list'),
    # path('blog/<slug:slug>/', views.ArticleBlogDetailView.as_view(), name='blog_detail'),
    # path('contact/', views.ContactView.as_view(), name='contact'),
]
