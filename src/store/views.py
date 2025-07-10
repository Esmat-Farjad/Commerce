from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import activate
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Count


from store.filters import ProductsFilter
from .models import BaseUnit, Category, Customer, OtherIncome, Products, SalesDetails, SalesProducts
from .forms import BaseUnitForm, CustomerForm, OtherIncomeForm, PurchaseForm, RegistrationForm
from .models import Category, Products
from .forms import PurchaseForm, RegistrationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate, login, logout
from datetime import date, timedelta
from django.utils import timezone

import random
import json
from django.http import HttpResponse, JsonResponse

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
    order_products = Products.objects.filter(num_of_packages__lt=10)
    today_date = date.today()
    sales_details = (
        SalesDetails.objects
        .filter(user=request.user, created_at__date=today_date)
        .aggregate(
            total_sale=Sum('total_amount'),
            total_paid=Sum('paid_amount'),
            total_unpaid=Sum('unpaid_amount'),
            total_customer=Count('customer', distinct=True)  # Ensure distinct customers are counted
        )
    )
    
    top_packages = (
        SalesProducts.objects
        .filter(sale_detail__user=request.user, sale_detail__created_at__date=today_date)
        .values('product__name','product__category__name')  # Group by product name
        .annotate(total_package_qty=Sum('package_qty'))  # Calculate total package quantity for each product
        .order_by('-total_package_qty')[:10]  # Order by total package quantity in descending order
    )
    context = {
        'top_packages':top_packages,
        'sales_details':sales_details,
        'order_products':order_products
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
            
        else:
            messages.error(request, _("Something Went wrong. Please fix the below error !"))
           
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
            # print(f"total_price: {total_package_price} || total_items: {stock} || item_sale_price: {item_sale_price}")
            purchase = form.save(commit=False)
            purchase.stock = stock
            purchase.item_sale_price = item_sale_price
            purchase.total_package_price= total_package_price
            purchase.user = request.user
            purchase.save()

            messages.success(request, "Product added successfully !")
            return redirect('purchase')
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

def update_products(request, pid):
    product = get_object_or_404(Products, pk=pid)

    form = PurchaseForm(instance=product)
    if request.method == 'POST':
        form = PurchaseForm(request.POST, request.FILES, instance=product)
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
    return render(request, 'purchase/purchase.html', context)

def delete_products(request, pid):
    product = get_object_or_404(Products, pk=pid)
    if product:
        product.delete()
        messages.success(request, _("Product deleted successfully"))
    return redirect("products_display")

def products_view(request):
    categories = Category.objects.all()
    customer = request.session.get('customer', {})
    customer_list = []
    products_queryset = Products.objects.select_related('category')

    products_filter = ProductsFilter(
        request.GET,
        request=request,
        queryset=products_queryset
    )

    # Handle session customer data
    if customer:  
        customer_list = list(customer.values())[0]

    # # Pagination
    # paginator = Paginator(products_filter.qs, 10)  # Show 10 products per page
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)
    context = {
        'products': products_filter.qs,
        'categories': categories,
        'filter_form': products_filter,
        'customer': customer_list
    }
    return render(request, 'sale/product_view.html', context)

def check_customer(request):
    code = request.GET.get("code")
    try:
        existing_customer = Customer.objects.get(id=code)
        customer_session = request.session.get('customer', {})
        customer_session[existing_customer.id] = existing_customer.name
        request.session['customer'] = customer_session
        form = CustomerForm(instance=existing_customer)
    except Customer.DoesNotExist:
        form = CustomerForm(initial={"code": code})
    return render(request, "partials/_customer_form.html", {"form": form})

def create_customer(request):
    form = CustomerForm()
    if request.method == 'POST':
        if 'ignore' in request.POST:
            customer, created = Customer.objects.get_or_create(
            name="متفرقه",
            phone="0000000",  # Put phone in quotes if it's a CharField
            defaults={"address": "------"}
            )

            existing_customer = get_object_or_404(Customer, pk=customer.id)
            customer_session = request.session.get('customer', {})
            customer_session[existing_customer.id] = existing_customer.name
            request.session['customer'] = customer_session
            return redirect('products-view')
        else:
            form = CustomerForm(request.POST)
            if form.is_valid():
                print("Form validation process................................................")
                new_customer = form.save()
                # Add to session
                customer_session = request.session.get('customer', {})
                customer_session[new_customer.id] = new_customer.name
                request.session['customer'] = customer_session
                # Notify user
                messages.success(request, _("Customer has been added successfully."))
                return redirect('products-view')
            else:
                messages.error(request, _("Something went wrong. Please fix the errors below."))
                print(f"Form errors: {form.errors}")

                
    else:
        form=CustomerForm()
        
    context = {
        'form':form
    }
    return render(request, 'sale/product_view.html', context)

def old_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer_session = request.session.get('customer', {})
    customer_session[customer.id] = customer.name
    request.session['customer'] = customer_session
    messages.success(request, _("Customer has been selected successfully."))
    return redirect('products-view')

def search_products(request):
    search = request.GET.get('search')
    products = Products.objects.select_related('category')
    product_list = (
        products.filter(category__name__istartswith=search) | products.filter(name__istartswith=search)
    )
    context = {
        'products':product_list
    }
    return render(request, 'partials/_search_list.html', context)


def remove_cart_item(request, pid):
    cart = request.session.get('cart', {})
    # Find the key of the item with the specified product_id
    item_key_to_remove = None
    for item_key, item in cart.items():
        if str(item['product_id']) == pid:
            item_key_to_remove = item_key
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

def print_invoice(request, sales_id):
    sales_details = get_object_or_404(SalesDetails, bill_number=sales_id)
    
    sales_product = SalesProducts.objects.filter(sale_detail=sales_details)

    calculate = sales_product.aggregate(
        total_amount=Sum('total_price')
    )
    context = {
        'sales_details':sales_details,
        'sales_products':sales_product,
        'calculate':calculate
    }
    return render(request, 'partials/_print_invoice.html', context)

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
                    user = request.user,
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
            request.session['customer'] = {}
            messages.success(request, "Products have been sold successfully!")
            return redirect("print-invoice",sales_details)
        except Exception as e:
            # Roll back the transaction and handle the error gracefully
            messages.error(request, f"An error occurred: {str(e)}")

    context = {
        'cart_details': cart_details,
        'grand_total': grand_total,
        'customer': customer_instance,
    }
    return render(request, 'sale/cart_view.html', context)

def sold_products_view(request):
    sales_details = SalesDetails.objects.select_related("customer").prefetch_related(
       "sale_detail"
    )
    if request.method == 'POST':
        bill_number = request.POST.get('bill-number')
        if bill_number:
            sales_details=sales_details.filter(bill_number=bill_number)

    context = {
        'sold_products':sales_details
    }
    return render(request, 'sale/sold_products_view.html', context)

def sold_product_detail(request, pk):
    sales_id = get_object_or_404(SalesDetails, pk=pk)
   
    sales_products = SalesProducts.objects.filter(sale_detail=pk).select_related('product')

    context = {
        'sales_products':sales_products,
        'sales_info':sales_id,
    }
    return render(request, 'sale/sold_products_detail.html', context)

def return_items(request, pk):
    # Get the returned product or raise 404
    returned_product = get_object_or_404(SalesProducts, id=pk)
    
    # Calculate new quantities
    returned_pkg = safe_int(returned_product.package_qty)
    returned_item = safe_int(returned_product.item_qty)
    product = returned_product.product  # Get the related product
    
    # Use atomic transaction to prevent race conditions
    with transaction.atomic():
        # Update product quantities
        product.num_of_packages = safe_int(product.num_of_packages) + returned_pkg
        product.num_items = safe_int(product.num_items) + returned_item
        product.save() 
        returned_product.delete()
        return HttpResponse('', headers={'HX-Trigger': 'returnSuccess'})

    



# dashboard contaner view
def income(request):
    form = OtherIncomeForm()
    today_date = date.today()
    other_income = OtherIncome.objects.filter(date_created=today_date)
    if request.method == 'POST':
        form = OtherIncomeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Income has been added successfully"))
        else:
            messages.error(request, _("Something went wrong. Please try again"))
    context = {
        'form':form,
        'other_income':other_income
    }
    return render(request, 'partials/management/_income-view.html', context)

def expense(request):
    return render(request, 'partials/management/_expense-view.html')

def summary(request):
    return render(request, 'partials/management/_summary-view.html')
def returned(request):
    return render(request, 'partials/management/_return-view.html')

def base_unit(request):
    form = BaseUnitForm()
    base_units = BaseUnit.objects.all()
    if request.method == 'POST':
        form = BaseUnitForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Unit has been saved successfully"))
            return redirect('base-unit')
        else:
            messages.error(request, _("Something went wrong. Please try again"))
    else:
        form = form
    context = {
        'form':form,
        'base_units':base_units
    }
    return render(request, 'partials/management/_base_unit-view.html',context)

def update_base_unit(request, unit_id):
    baseunit = get_object_or_404(BaseUnit, pk=unit_id)
    base_units = BaseUnit.objects.all()
    if request.method == 'POST':
        form = BaseUnitForm(request.POST, instance=baseunit)
        if form.is_valid():
            form.save()
            messages.success(request, _("Unit has been updated successfully"))
            return redirect('base-unit')
        else:
            messages.error(request, _("Something went wrong. Please try again"))
    else:
        form = BaseUnitForm(instance=baseunit)

    context = {
        'form': form,
        'base_units': base_units
    }
    return render(request, 'partials/management/_base_unit-view.html', context)

def delete_base_unit(request, unit_id):
    baseunit = get_object_or_404(BaseUnit, pk=unit_id)
    # Delete the object
    deleted_count = baseunit.delete()  # delete() returns (number_of_deleted_objects, details)
    # Check if the object was deleted successfully
    if deleted_count:
        messages.success(request, _("Unit has been deleted successfully"))
    else:
        messages.error(request, _("Unable to delete the unit"))
    
    # Redirect to the base-unit page
    return redirect('base-unit')

def customer(request):
    customers = Customer.objects.all()
    # Add customer sales details (paid, unpaid, bill count) for each customer
    if request.method == 'POST':
        phone = request.POST.get('phone')
        customers = customers.filter(phone=phone)
    customer_data = []
    for customer in customers:
        sales_data = SalesDetails.objects.filter(customer=customer).aggregate(
            total_amount=Sum('total_amount'),
            total_paid=Sum('paid_amount'),
            total_unpaid=Sum('unpaid_amount'),
            bill_count=Count('bill_number')
        )
        customer_data.append({
            'customer': customer,
            'total_amount':sales_data['total_amount'] or 0, 
            'total_paid': sales_data['total_paid'] or 0,  # Default to 0 if None
            'total_unpaid': sales_data['total_unpaid'] or 0,  # Default to 0 if None
            'bill_count': sales_data['bill_count'],
        })
    

    context = {
        'customer_data':customer_data
    }
    return render(request, 'partials/management/_customer-view.html', context)

def sales_dashboard(request):
    return redirect('summary')

def create_payment(request, cid):
    customer = get_object_or_404(Customer, pk=cid)
    pass