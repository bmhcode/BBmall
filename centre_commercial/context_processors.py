from .models import Order, Wishlist

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
    nbr_wishlist = 0
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user).first()
        if wishlist:
            nbr_wishlist = wishlist.products.count()

    return {
        'nbr_wishlist': nbr_wishlist
    }