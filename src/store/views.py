from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import activate
from django.conf import settings
from django.contrib import messages
from .models import Category, Products
from .forms import PurchaseForm, RegistrationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate, login, logout
from datetime import datetime, timedelta
from django.utils import timezone
import random
import json
from django.http import JsonResponse

# Create your views here.
def switch_language(request, lang_code):
    if lang_code in dict(settings.LANGUAGES):  # ✅ Ensure the language is valid
        activate(lang_code)
        request.session['django_language'] = lang_code  # ✅ Store in session
        # ✅ Store the language in a cookie
        response = redirect(request.META.get('HTTP_REFERER', '/'))
        response.set_cookie('django_language', lang_code, max_age=31536000)  # 1 year
        return response
    return redirect('/')

def landing(request):    
    return render(request, 'landing-page.html')

def Home(request):
    today = timezone.now().date()
    last_7_days = [(today - timedelta(days=i)).strftime('%a') for i in range(6, -1, -1)]
    last_7_day_sales = [random.randint(50, 300) for _ in range(7)] 

    context = {
        'today_sales': 500,
        'today_products_sold': 120,
        'today_agreements': 18,
        'last_7_days': last_7_days,
        'last_7_day_sales': last_7_day_sales,
    }
    return render(request, 'home.html', context)

def signin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST.get('password')
        user = authenticate(request, username=email, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, _("Welcome !"))
            return redirect('home')
        else:
            messages.error(request, _("Invalid username or password"))
    return render(request, 'auth/login.html')

def signup(request):
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("The user has been registered successfully"))
            print("user created")
        else:
            messages.error(request, _("Something Went wrong. Please fix the below error !"))
            print("something went wrong")
    register_form = form
    context = {
        'form':register_form
    }
    return render(request, 'auth/register.html', context)

def signout(request):
    logout(request) 
    return redirect('sign-in') 

def purchase(request):
    purchase_form = PurchaseForm()
    if request.method == 'POST':
        purchase_form = PurchaseForm(request.POST, request.FILES)
        
        if purchase_form.is_valid():
            package_purchase_price = purchase_form.cleaned_data['package_purchase_price']
            package_contain = purchase_form.cleaned_data.get('package_contain')
            num_of_packages = purchase_form.cleaned_data.get('num_of_packages')
            total_package_price = purchase_form.cleaned_data.get('total_package_price')
            package_sale_price = purchase_form.cleaned_data.get('package_sale_price')
            total_package_price = int(num_of_packages) * int(package_purchase_price)
            total_items = int(package_contain) * int(num_of_packages)
            item_sale_price = round((package_sale_price / package_contain), 3) if package_contain else 0
            print(f"total_price: {total_package_price} || total_items: {total_items} || item_sale_price: {item_sale_price}")
            purchase = purchase_form.save(commit=False)
            purchase.total_items = total_items
            purchase.item_sale_price = item_sale_price
            purchase.total_package_price= total_package_price
            purchase.user = request.user
            purchase.save()

            messages.success(request, "Product added successfully !")
            # return redirect("product_list")
        else:
            messages.error(request, f"Something went wrong. Please fix the below errors.{purchase_form.errors}")
        
    purchase = Products.objects.all().order_by('-id')
    #Paginator start
    p = Paginator(purchase, 14 )
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)
    #Paginator end
    number = []
    for x in range(1, 100,1):
        number.append(x)
    cat = Category.objects.all()
    context = {
        'category':cat,
        'page_obj':page_obj,
        'num':number,
        'form':purchase_form
        }
    return render(request, 'purchase/purchase.html', context)

def products_display(request):
    product = Products.objects.all().order_by('-id')
    p = Paginator(product, 14)
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)
    # paginator end
    context = {'page_obj':page_obj,'flag':'list'}
    return render(request, 'purchase/product.html', context)


def products_view(request):
    products = Products.objects.all()
    categories = Category.objects.all()
    
    context ={
        'products':products,
        'categories':categories,
        
    }
    return render(request, 'sale/product_view.html',context)

# add to cart
def add_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        item_quantity = data.get('item_quantity')
        package_quantity = data.get('package_quantity')
        item_price = data.get('item_price')
        package_price = data.get('package_price')
        
        try:
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)
        
        cart = request.session.get('cart', {})
        item_key = f"{product_id}_item"
        if item_key in cart:
            cart[item_key]['item_quantity'] = item_quantity
            cart[item_key]['package_quantity'] = package_quantity
            cart[item_key]['item_price'] = item_price
            cart[item_key]['package_price'] = package_price
        else:
            cart[item_key] = {
                'product_id':product.id,
                'item_quantity':item_quantity,
                'package_quantity':package_quantity,
                'item_price':item_price,
                'package_price':package_price
            }
        request.session['cart'] = cart  # Save cart back into session
        number_of_added_item = len(request.session['cart'])

        return JsonResponse({'status':200, 'message':'success','cart_length':number_of_added_item})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def cart_view(request):
    cart = request.session.get('cart', {})
    cart_details = []
    grand_total = 0
    for key, item in cart.items():
        product = get_object_or_404(Products, pk=item['product_id'])
        item_quantity = int(item.get('item_quantity') or 0)
        package_quantity = int(item.get('package_quantity') or 0)
        item_price = int(item.get('item_price') or 0)
        package_price = int(item.get('package_price') or 0)

        sub_total = (item_quantity * item_price) + (package_quantity * package_price)
        grand_total = grand_total + sub_total
        print(f"subtotal: {sub_total} adn Grand total: {grand_total}")
        cart_details.append({
            'product': product,
            'item_quantity': item['item_quantity'],
            'package_quantity': item['package_quantity'],
            'item_price': item['item_price'],
            'package_price': item['package_price'],
            'sub_total':sub_total,
        })
    context = {
        'cart_details':cart_details,
        'grand_total':grand_total
    }
    return render(request, 'sale/cart_view.html', context)

def remove_cart_item(request, pid):
    cart = request.session.get('cart', {})
    # Find the key of the item with the specified product_id
    item_key_to_remove = None
    for item_key, item in cart.items():
        if str(item['product_id']) == pid:
            item_key_to_remove = item_key
            print(f"item to remove: {item_key_to_remove}")
            break

    # Remove the item from the cart if found
    if item_key_to_remove:
        del cart[item_key_to_remove]

        # Update the session
        request.session['cart'] = cart
    return redirect('cart-view')