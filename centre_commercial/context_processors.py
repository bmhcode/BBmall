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
    if request.user.is_authenticated and hasattr(request.user, 'wishlist'):
        return {
            'wishlist_count': request.user.wishlist.products.count()
        }
    return {'wishlist_count': 0}

