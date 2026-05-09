from .models import Order, Wishlist
# from django.core.cache import cache

def cart_processor(request):
    cart_count = 0
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, status='pending').first()
        if order:
            # sum quantities
            cart_count = sum(item.quantity for item in order.items.all())
    return {
        'cart_count': cart_count
    }

def wishlist_processor(request):

    wishlist_count = 0
    mall_slug = None

    if request.user.is_authenticated:
        wishlist = getattr(request.user, 'wishlist', None)
        if wishlist:
            wishlist_count = wishlist.products.count()

    if request.resolver_match:
        mall_slug = request.resolver_match.kwargs.get('mall_slug')

    return {
        'wishlist_count': wishlist_count,
        'mall_slug': mall_slug
    }