from django.urls import path
from . import views

urlpatterns = [
    # Portal — choose your mall (root page)
    path('', views.HomeView.as_view(), name='home'),
    
    # Mall Management CRUD
    path('malls/',         views.MallListView.as_view(),   name='mall_list'),
    path('malls/add/',     views.MallCreateView.as_view(), name='mall_create'),
    path('malls/<slug:slug>/edit/',   views.MallUpdateView.as_view(), name='mall_update'),
    path('malls/<slug:slug>/delete/', views.MallDeleteView.as_view(), name='mall_delete'),

    path('mall/<slug:slug>/', views.MallView.as_view(), name='mall'),

    # Individual mall homepage (the "Entered" mall experience)
    # path('magasins/', views.MagasinListView.as_view(), name='magasin_list'),
    # path('magasin/<slug:slug>/', views.MagasinDetailView.as_view(), name='magasin_detail'),
    # path('evenements/', views.EvenementListView.as_view(), name='evenement_list'),
    # path('evenements/<slug:slug>/', views.EvenementDetailView.as_view(), name='evenement_detail'),
    # path('promotions/', views.PromotionListView.as_view(), name='promotion_list'),
    # path('blog/', views.ArticleBlogListView.as_view(), name='blog_list'),
    # path('blog/<slug:slug>/', views.ArticleBlogDetailView.as_view(), name='blog_detail'),
    # path('contact/', views.ContactView.as_view(), name='contact'),

    path('magasins/', views.MagasinListView.as_view(), name='magasin_list_all'),
    path('mall/<slug:slug>/magasins/', views.MagasinListView.as_view(), name='magasin_list_by_mall'),

    path('magasin/<slug:slug>/', views.MagasinDetailView.as_view(), name='magasin_detail'),





    path('evenements/', views.EvenementListView.as_view(), name='evenement_list'),
    path('evenements/<slug:slug>/', views.EvenementDetailView.as_view(), name='evenement_detail'),
    path('promotions/', views.PromotionListView.as_view(), name='promotion_list'),
    path('blog/', views.ArticleBlogListView.as_view(), name='blog_list'),
    path('blog/<slug:slug>/', views.ArticleBlogDetailView.as_view(), name='blog_detail'),
    path('contact/', views.ContactView.as_view(), name='contact'),


    
]
