import django_filters
from .models import Products,Category
from django import forms

class ProductsFilter(django_filters.FilterSet):
    category = django_filters.ModelMultipleChoiceFilter(
        queryset = Category.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "input-field"})
    )
    class Meta:
        model = Products
        fields = ["category"]