from django.db import models
from django.contrib.auth.models import User
import uuid
# Create your models here.



class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Products(models.Model):
    NUMBER_CHOICES = [(i, str(i)) for i in range(1,201)]
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    code = models.IntegerField(null=True, default=0)
    name = models.CharField(max_length=100)
    package_contain = models.PositiveBigIntegerField(choices=NUMBER_CHOICES)
    package_purchase_price = models.IntegerField(default=0, null=True)
    total_package_price = models.IntegerField(default=0, null=True)     
    num_of_packages = models.IntegerField(default=1)
    package_sale_price = models.IntegerField(null=True, default=0)
    item_sale_price = models.IntegerField( null=True ,default=0)
    num_items = models.IntegerField(null=True,default=0)
    stock = models.IntegerField()
    image = models.ImageField(default='default.png', upload_to='item_images')
    description = models.TextField(max_length=200,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return self.name
    
class Customer(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    phone = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name

class BillNumberTracker(models.Model):
    current_number = models.PositiveIntegerField(default=1001)

    @classmethod
    def get_next_bill_number(cls):
        # Get or create the tracker instance
        tracker, created = cls.objects.get_or_create(id=1)
        # Increment the counter
        next_number = tracker.current_number
        tracker.current_number += 1
        tracker.save()
        return next_number   


class SalesDetails(models.Model):
    user = models.ForeignKey(User, related_name='user',null=True, blank=True, on_delete=models.SET_NULL)
    bill_number = models.CharField(max_length=100, unique=True, editable=False, default="")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="customer")
    total_amount = models.CharField(max_length=200,null=True, blank=True)
    paid_amount = models.CharField(max_length=200,null=True, blank=True, default="0")
    unpaid_amount = models.CharField(max_length=200,null=True, blank=True, default="0")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Generate a unique bill number if not already set
        if not self.bill_number:
            self.bill_number = str(BillNumberTracker.get_next_bill_number())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.bill_number

class SalesProducts(models.Model):
    sale_detail = models.ForeignKey(SalesDetails, related_name='sale_detail',on_delete=models.CASCADE)
    product = models.ForeignKey(Products, related_name='produts', null=True,blank=True, on_delete=models.SET_NULL)
    item_price = models.CharField(max_length=200, null=True, blank=True)
    package_price = models.CharField(max_length=200, null=True, blank=True)
    item_qty = models.CharField(max_length=200, null=True, blank=True)
    package_qty = models.CharField(max_length=200, null=True, blank=True)
    total_price = models.CharField(max_length=200, null=True, blank=True)
    
    def __str__(self):
        return f"bill number {self.sale_detail}"
    


class OtherIncome(models.Model):
    date_created = models.DateField()
    source = models.CharField(max_length=255)  # like 'Commission', 'Asset Sale'
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.source

class Expense(models.Model):
    date_created = models.DateField()
    category = models.CharField(max_length=255)  # like 'Rent', 'Salaries', 'Car Fare'
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.category