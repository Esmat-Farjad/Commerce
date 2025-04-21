from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import activate
from django.conf import settings
from django.contrib import messages
from django.db import transaction

from store.filters import ProductsFilter
from .models import Category, Customer, Products, SalesDetails, SalesProducts
from .forms import CustomerForm, PurchaseForm, RegistrationForm
from .models import Category, Products
from .forms import PurchaseForm, RegistrationForm, UpdateProductForm
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

def root_view(request):
    if request.user.is_authenticated:  # Check if the user is authenticated
        return redirect('home')  # Redirect to the 'home' page
    else:
        return redirect("landing")

def landing(request):    
    return render(request, "landing-page.html")

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
    form = PurchaseForm()
    if request.method == 'POST':
        form = PurchaseForm(request.POST, request.FILES)
        
        if form.is_valid():
            package_purchase_price = form.cleaned_data['package_purchase_price']
            package_contain = form.cleaned_data.get('package_contain')
            num_of_packages = form.cleaned_data.get('num_of_packages')
            total_package_price = form.cleaned_data.get('total_package_price')
            package_sale_price = form.cleaned_data.get('package_sale_price')
            total_package_price = int(num_of_packages) * int(package_purchase_price)
            stock = int(package_contain) * int(num_of_packages)
            item_sale_price = round((package_sale_price / package_contain), 3) if package_contain else 0
            print(f"total_price: {total_package_price} || total_items: {stock} || item_sale_price: {item_sale_price}")
            purchase = form.save(commit=False)
            purchase.stock = stock
            purchase.item_sale_price = item_sale_price
            purchase.total_package_price= total_package_price
            purchase.user = request.user
            purchase.save()

            messages.success(request, "Product added successfully !")
            # return redirect("product_list")
        else:
            messages.error(request, f"Something went wrong. Please fix the below errors.{form.errors}")
        
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
        'form':form
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

def manage_product(request, action, pid):
    product = get_object_or_404(Products, pk=pid)
    
    if action == 'edit':
        form = UpdateProductForm(instance=product)
        if request.method == 'POST':
            form = UpdateProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                package_purchase_price = form.cleaned_data['package_purchase_price']
                package_contain = form.cleaned_data.get('package_contain')
                num_of_packages = form.cleaned_data.get('num_of_packages')
                package_sale_price = form.cleaned_data.get('package_sale_price')

                total_package_price = int(num_of_packages) * int(package_purchase_price)
                total_items = int(package_contain) * int(num_of_packages)
                item_sale_price = round((package_sale_price / package_contain), 3) if package_contain else 0

                product = form.save(commit=False)
                product.total_items = total_items
                product.item_sale_price = item_sale_price
                product.total_package_price = total_package_price
                product.save()

                messages.success(request, "Product updated successfully.")
                return redirect("products_display")
            else:
                messages.error(request, f"Form has error: {form.errors}")

        context = {
            'product': product,
            'form': form
        }
        return render(request, 'purchase/product_update.html', context)
    
    elif action == 'delete':
        product.delete() 
        messages.success(request, "Product deleted successfully.")
        return redirect("products_display")

def products_view(request):
    categories = Category.objects.all()
    customer = request.session.get('customer', {})
    customer_list = []
    products_filter = ProductsFilter(
        request.GET,
        request=request,
        queryset = Products.objects.select_related('category')
    )
    customer_form = CustomerForm()
    if request.method == 'POST':
        customer_form = CustomerForm(request.POST)
        if customer_form.is_valid():
            new_customer = customer_form.save()
            customer[new_customer.id] = new_customer.name
            request.session['customer'] = customer
            messages.success(request, _("Customer has been added successfuly"))
    if customer:  
        customer_list = list(customer.values())[0]
    context ={
        'products':products_filter.qs,
        'categories':categories,
        'filter_form':products_filter,
        'form':customer_form,
        'customer':customer_list
    }
    return render(request, 'sale/product_view.html',context)

# add to cart
# def add_to_cart(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         product_id = data.get('product_id')
#         item_quantity = data.get('item_quantity')
#         package_quantity = data.get('package_quantity')
#         item_price = data.get('item_price')
#         package_price = data.get('package_price')
        
#         try:
#             product = Products.objects.get(id=product_id)
#         except Products.DoesNotExist:
#             return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)
        
#         cart = request.session.get('cart', {})
#         item_key = str(product_id)
#         if item_key in cart:
#             cart[item_key]['item_quantity'] = item_quantity
#             cart[item_key]['package_quantity'] = package_quantity
#             cart[item_key]['item_price'] = item_price
#             cart[item_key]['package_price'] = package_price
#         else:
#             cart[item_key] = {
#                 'product_id':product_id,
#                 'item_quantity':item_quantity,
#                 'package_quantity':package_quantity,
#                 'item_price':item_price,
#                 'package_price':package_price
#             }
#         request.session['cart'] = cart  # Save cart back into session
#         number_of_added_item = len(request.session['cart'])

#         return JsonResponse({'status':200, 'message':'success','cart_length':number_of_added_item})
#     return JsonResponse({'error': 'Invalid request'}, status=400)


# def cart_view(request):
#     cart = request.session.get('cart', {})
#     customer = request.session.get('customer',{})
#     cart_details = []
#     grand_total = 0
#     sold_stock = 0
#     product_update_stock = []
#     # Fetch all products in a single query to optimize performance
#     product_ids = [item['product_id'] for key, item in cart.items()]
#     products = Products.objects.filter(pk__in=product_ids)
#     product_mapping = {product.id: product for product in products}
#     print(product_mapping)
#     for key, item in cart.items():

#         product = get_object_or_404(Products, pk=item['product_id'])
#         item_quantity = int(item.get('item_quantity') or 0)
#         package_quantity = int(item.get('package_quantity') or 0)
#         item_price = int(item.get('item_price') or 0)
#         package_price = int(item.get('package_price') or 0)

#         # Calculations of new stock
#         sold_stock = (int(package_quantity) * int(product.package_contain)) + int(item_quantity)
#         new_stock = product.stock - sold_stock

#         # Prepare records for bulk update
#         product.stock = new_stock
#         product.num_of_packages = int(new_stock) // int(product.package_contain)
#         product.num_items = int(new_stock) % int(product.package_contain)
#         product_update_stock.append(product)

#         # Calculate subtotal and append to cart details
#         sub_total = (item_quantity * item_price) + (package_quantity * package_price)
#         grand_total += sub_total
#         cart_details.append({
#             'product': product,
#             'item_quantity': item_quantity,
#             'package_quantity': package_quantity,
#             'item_price': item_price,
#             'package_price': package_price,
#             'sub_total': sub_total,
#         })
#     customer_instance = None
#     if customer:
#         customer_pk= list(customer.keys())[0]
#         customer_instance = get_object_or_404(Customer, pk=customer_pk)
#     if request.method == 'POST':
#         unpaid_amount = grand_total
#         paid_amount =request.POST.get('paid')
#         if paid_amount:
#             unpaid_amount = int(grand_total) - int(paid_amount)
#         # Create a SalesDetails instance
#         sales_details = SalesDetails.objects.create(
#             customer=customer_instance,
#             total_amount=grand_total, 
#             paid_amount=paid_amount,    
#             unpaid_amount=unpaid_amount,  
#         )
#         # Use atomic transaction for bulk operations
#         with transaction.atomic():
#             # Perform bulk update
#             Products.objects.bulk_update(product_update_stock, ['stock', 'num_of_packages', 'num_items'])

#             # If you want to bulk create cart details in another model, e.g., SalesProducts
#             sales_products = []

#             for item in cart_details:
#                 sales_product = SalesProducts(
#                     sale_detail=sales_details,  # Replace with actual instance
#                     item_price=item['item_price'],
#                     package_price=item['package_price'],
#                     item_qty=item['item_quantity'],
#                     package_qty=item['package_quantity'],
#                     total_price=item['sub_total'],
#                 )
#                 sales_products.append(sales_product)

#             # Bulk create the SalesProducts
#             created_sales_products = SalesProducts.objects.bulk_create(sales_products)

#             # Associate products with the created SalesProducts
#             for item, sales_product in zip(cart_details, created_sales_products):
#                 print("THIS IS THE ITEM", item)
#                 product_instance = product_mapping[item['product'].id]
#                 sales_product.product.set([product_instance])  # Use set() to assign ManyToManyField
#             messages.success(request, "Product has been sold")


#     print(f"THIS IS THE CART DETAILS: {cart_details}")
#     context = {
#         'cart_details':cart_details,
#         'grand_total':grand_total,
#         'customer':customer_instance
#     }
#     return render(request, 'sale/cart_view.html', context)

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

# Add to Cart
def add_to_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON body'}, status=400)

        # Extract data
        product_id = data.get('product_id')
        item_quantity = data.get('item_quantity', 0)
        package_quantity = data.get('package_quantity', 0)
        item_price = data.get('item_price', 0)
        package_price = data.get('package_price', 0)

        # Validate product existence
        product = Products.objects.filter(id=product_id).first()
        if not product:
            return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)

        # Retrieve cart from session and update it
        cart = request.session.get('cart', {})
        cart[str(product_id)] = {
            'product_id': product_id,
            'item_quantity': item_quantity,
            'package_quantity': package_quantity,
            'item_price': item_price,
            'package_price': package_price,
        }
        request.session['cart'] = cart  # Save updated cart back into session

        return JsonResponse({"status": 200, "message": "success", "cart_length": len(cart)})
    
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

def safe_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
    
def cart_view(request):
    # Retrieve cart and customer from session
    cart = request.session.get('cart', {})
    customer_session = request.session.get('customer', {})
    cart_details = []
    product_update_stock = []
    grand_total = 0

    if not cart:
        return render(request, 'sale/cart_view.html', {'cart_details': [], 'grand_total': 0, 'customer': None})

    # Fetch all products at once
    product_ids = [item['product_id'] for item in cart.values()]
    products = Products.objects.filter(pk__in=product_ids).select_related()
    product_mapping = {product.id: product for product in products}

    # Build cart details
    for item in cart.values():
        product = product_mapping.get(safe_int(item.get('product_id')))
        if not product:
            continue

        item_quantity = safe_int(item.get('item_quantity'))
        package_quantity = safe_int(item.get('package_quantity'))
        item_price = safe_int(item.get('item_price'), 0)
        package_price = safe_int(item.get('package_price'), 0)

        # Calculate stock updates
        package_contain = safe_int(product.package_contain, 1)  # Default to 1 to avoid division by zero
        sold_stock = (package_quantity * package_contain) + item_quantity
        new_stock = safe_int(product.stock) - sold_stock
        product.stock = new_stock
        product.num_of_packages = new_stock // package_contain
        product.num_items = new_stock % package_contain
        product_update_stock.append(product)

        # Calculate subtotal and cart details
        sub_total = (item_quantity * item_price) + (package_quantity * package_price)
        grand_total += sub_total
        cart_details.append({
            'product': product,
            'item_quantity': item_quantity,
            'package_quantity': package_quantity,
            'item_price': item_price,
            'package_price': package_price,
            'sub_total': sub_total,
        })

    # Retrieve customer instance
    customer_instance = None
    if customer_session:
        customer_pk = list(customer_session.keys())[0]
        customer_instance = Customer.objects.filter(pk=customer_pk).first()

    # Handle sale submission
    if request.method == 'POST':
        try:
            paid_amount = safe_int(request.POST.get('paid', 0))
            unpaid_amount = grand_total - paid_amount

            # Create SalesDetails instance
            with transaction.atomic():
                sales_details = SalesDetails.objects.create(
                    customer=customer_instance,
                    total_amount=grand_total,
                    paid_amount=paid_amount,
                    unpaid_amount=unpaid_amount,
                )

                # Bulk update product stock
                Products.objects.bulk_update(product_update_stock, ['stock', 'num_of_packages', 'num_items'])

                # Bulk create SalesProducts
                sales_products = [
                    SalesProducts(
                        sale_detail=sales_details,
                        product=item['product'],  # Directly use the product instance
                        item_price=item['item_price'],
                        package_price=item['package_price'],
                        item_qty=item['item_quantity'],
                        package_qty=item['package_quantity'],
                        total_price=item['sub_total'],
                    ) for item in cart_details
                ]
                SalesProducts.objects.bulk_create(sales_products)

            # Clear cart after successful sale
            request.session['cart'] = {}
            messages.success(request, "Products have been sold successfully!")
            return redirect("home")
        except Exception as e:
            # Roll back the transaction and handle the error gracefully
            messages.error(request, f"An error occurred: {str(e)}")

    context = {
        'cart_details': cart_details,
        'grand_total': grand_total,
        'customer': customer_instance,
    }
    return render(request, 'sale/cart_view.html', context)