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
]