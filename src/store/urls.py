from django.urls import path, include
from . import views

urlpatterns = [
    path('',views.root_view, name='root-view'),
    path("landing/", views.landing, name='landing'),
    path('home/', views.Home, name='home'),
    path('purchase/', views.purchase, name='purchase'),
    path(
        'language/switch/<str:lang_code>',
        views.switch_language,
        name="switch-language",
        ),
    path(
        'auth/sign-in',
        views.signin,
        name='sign-in',
    ),
    path(
        'auth/sign-up',
        views.signup,
        name='sign-up',
    ),
    path(
        'auth/sign-out',
        views.signout,
        name="sign-out",
    ),
    # sale page
    path(
        'products/sale',
        views.products_view,
        name='products-view'
    ),
    # Add product to cart
    path(
        'product/add',
        views.add_to_cart,
        name='add-to-cart',
    ),
    path(
        'sale/cart',
        views.cart_view,
        name='cart-view',
    ),
    path(
        'sale/cart/delete/<str:pid>',
        views.remove_cart_item,
        name='remove-cart-item',
    ),
    path(
        'product/list', 
        views.products_display,
        name='products_display'
    ),
    path (
        'product/<str:action>/<int:pid>',
        views.manage_product,
        name = 'manage_product'
    ),
    path(
        'product/sold',
        views.sold_products_view,
        name="sold-products-view",
    ),
    path(
        'product/sold/detail/<str:pk>',
        views.sold_product_detail,
        name='sold-product-detail',
    ),
]