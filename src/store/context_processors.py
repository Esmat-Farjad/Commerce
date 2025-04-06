def cart_context(request):
    cart = request.session.get('cart', {})
    cart_length = None
    if len(cart) > 0:
        cart_length = len(request.session['cart'])
    return {
        'cart_length': cart_length
    }