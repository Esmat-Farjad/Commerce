from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.Home, name='home'),
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