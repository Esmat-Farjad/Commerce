from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from .models import Category, Purchase

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = "__all__"
        exclude = ['user','total_items','total_package_price', 'item_sale_price']
        
    def __init__(self, *args, **kwargs):
        super(PurchaseForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class']="form-input"
            visible.field.widget.attrs['placeholder']=visible.field.label