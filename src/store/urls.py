from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
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
]