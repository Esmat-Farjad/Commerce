from django import forms
from .models import BaseUnit, ExchangeRate, OtherIncome, Products, Customer
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

# forms.py
class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Products
        exclude = ['stock', 'total_package_price', 'item_sale_price', 'usd_package_sale_price']
    
    def __init__(self, *args, **kwargs):
        super(PurchaseForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = "form-input-field"
            visible.field.widget.attrs['placeholder'] = _(visible.field.label)

class ExchangeRateForm(forms.ModelForm):
    class Meta:
        model = ExchangeRate
        fields = "__all__"
        widgets = {
            'usd_to_afn': forms.NumberInput(attrs={'step': '0.01', 'class': 'input-field'}),
        }
class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]
        labels = {
            'username': _('Username'),
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'email': _("Email"),
            'password1': _("Password"),
            'password2': _("Confrim Password")
        }
    
    def clean_username(self):
        """check if username already exists"""
        username = self.cleaned_data.get("username")
        qs = User.objects.filter(username__iexact=username)
        if qs.exists():
            raise forms.ValidationError(f"Username {username} already exists, please choose another.")
        return username

    def clean_email(self):
        """check if email already exists"""
        email = self.cleaned_data.get("email")
        qs = User.objects.filter(email__iexact=email)
        if qs.exists():
            raise forms.ValidationError(f"Email {email} already exists, please choose another.")
        return email
        
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'input-field'

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = "__all__"
    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'input-field'


class OtherIncomeForm(forms.ModelForm):
    class Meta:
        model = OtherIncome
        field = "__all__"
        exclude = ()

        
    def __init__(self, *args, **kwargs):
        super(OtherIncomeForm, self).__init__(*args, **kwargs)
        self.fields['date_created'].widget = forms.DateInput(
                attrs={
                    'type': 'date',  # HTML5 date input type
                    'class': 'date-picker',  # Additional class for styling
                }
            )
        # Add the 'jalali-date-picker' class to the date_created field
        if 'date_created' in self.fields:
            self.fields['date_created'].widget.attrs.update({
                'class': 'jalali-date-picker input-field',
                'autocomplete': 'off',  # Disable browser autocomplete
            })
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = "input-field"
            visible.field.widget.attrs['placeholder'] = _(visible.field.label)


class BaseUnitForm(forms.ModelForm):
    class Meta:
        model = BaseUnit
        fields = "__all__"
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(BaseUnitForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'input-field'
            visible.field.widget.attrs['placeholder'] = _(visible.field.label)