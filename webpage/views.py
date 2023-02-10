from django.shortcuts import render, redirect
from . models import User, Customer, ProductList, AddedToCart, Orders, Logo
import datetime
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import uuid
from django.db.models import Q , Sum
from django.http import FileResponse
import xlsxwriter
import io
from openpyxl.workbook import workbook
from json import dumps

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
# execute the line below after entering the virtual environment if and only if you reinstalled the venv (remove #)
# pip install django django-pwa xlsxwriter openpyxl pillow



# def hex_to_rgb(hex):
#     hex = hex[1:len(hex)] #this line of code will remove the # of the hex at the index[0]
#     rgb = []
#     for i in (0, 2, 4):
#         decimal = int(hex[i:i+2], 16)
#         rgb.append(decimal)

#     rgb_color = 'rgb' + str(tuple(rgb)) # this code will return rgb value
#     return rgb_color[0:len(rgb_color)-1] # this line will remove the close parenthesis of the rgb value



# Create your views here.

def home(request):
    all_user_containing_food_stall_names = User.objects.filter(is_superuser = True).all()


    all_products = ProductList.objects.filter().all()

    return render(request,'about/home.html', {"superusers" : all_user_containing_food_stall_names, 'all_products' : all_products})

def about(request):
    return render (request,'about/about.html')  


def add_product(request):

    if request.user.is_superuser:

        if request.method == 'POST':
            product_image = request.FILES['product_image']
            product_name = request.POST.get('product_name')
            product_price = request.POST.get('product_price')
            stocks = request.POST.get('stocks')

        try:

            if product_image.name.endswith('jpg') or product_image.name.endswith('jpeg') or product_image.name.endswith('svg') or product_image.name.endswith('png'):
                if not int(product_price) is None and not int(stocks) is None :
                    new_product = ProductList.objects.create(stall_owner = request.user,
                                                                product_id = product_name,
                                                                product_image = product_image,
                                                                product_price = int(product_price),
                                                                product_name = product_name,
                                                                stocks = int(stocks)                
                    )
                    new_product.save()
                    messages.info(request, 'A new product has been added.')
                else:
                    messages.info(request, 'You entered an invalid value for product price or product stocks')
            
            else:
                messages.info(request, 'The file that you attached is in invalid format. Please make sure that it is in jpg, jpeg, png, or svg file format.')

        except Exception as e:
            print(e)

    else:
        messages.info(request, 'The page you are trying to access is not available for your account type.')
        return redirect('home.html')

    return render(request, 'product_details/add_product.html')

def filtered_menu(request, stall_name):


    stall_owner = Customer.objects.filter(stall_name = stall_name).first()
    
    user_owner = User.objects.filter(username = stall_owner.user.username).first()

    product_list = ProductList.objects.filter(stall_owner = user_owner).all()

    if request.method == 'POST':
        product_price = request.POST.get('product_price')
        product_name  = request.POST.get('product_name')
        stall_owner = request.POST.get('stall_owner')
        qty = request.POST.get('qty')


        try:
            owner = User.objects.filter(username = stall_owner).first()
            product_added = ProductList.objects.filter(stall_owner = owner, product_name = product_name, product_price = str(product_price)).first()
            added_to_cart = AddedToCart.objects.create(customer = request.user.customer, 
                                                        product = product_added,
                                                        quantity = str(qty),
                                                        cart_id = str(uuid.uuid4()),
                                                        date_added = datetime.datetime.now())
            added_to_cart.save()
            messages.info(request, f'{product_name} has been added to your cart.')
            return redirect(f'menu-{stall_name}.html#{product_name}')


        except Exception as e:
            print(e)


    return render(request, 'product_details/filtered_menu.html', {'stall_name' : stall_name, 'product_list' : product_list})


def contact(request):
    return render(request,'about/contact.html')

def search(request):
    caller = ''
    searched_results = ''


    if request.method == 'POST':
        search = request.POST['search']



        searched_product = ProductList.objects.filter(product_name__contains = search).all()
        searched_stall = Customer.objects.filter(stall_name__contains = search).all()
      
        if searched_product:
            caller = 'product'
            searched_results = searched_product
        
        elif searched_stall:
            caller = 'stall'
            searched_results = searched_stall



    return render (request,'about/search.html', {'caller' : caller, 'searched_results' : searched_results})      


def orders(request):
    if not request.user.is_authenticated:
        messages.info(request, 'The page you are trying to access is not available. Please log in order to proceed thank you.')
        return redirect('login.html')
        
    my_orders = Orders.objects.filter(customer = request.user.customer).all()
    return render(request, 'dashboard/orders.html', {'my_orders' : my_orders})


def menu(request):
    all_products = ProductList.objects.filter().all()
    stall = Customer.objects.filter(~Q(stall_name = None)).all()

    return render (request,'dashboard/menu.html', {'stall' : stall, 'all_products' : all_products})
    
def cart(request):
    if not request.user.is_authenticated:
        messages.info(request, 'The page you are trying to access is not available. Please log in order to proceed thank you.')
        return redirect('login.html')

    my_cart = AddedToCart.objects.filter(customer = request.user.customer, is_pending = True, is_ordered = False).all().order_by('-date_added')

    if request.method == 'POST':
        cart_id = request.POST.get('cart_id')
        
        if cart_id:
            remove_product = AddedToCart.objects.filter(cart_id = cart_id).first()
            remove_product.delete()
            messages.info(request, f'The product has been removed from your cart.')
            return redirect('cart.html')

    return render (request,'dashboard/cart.html', {'my_cart' : my_cart})

def view_cart(request):
    total_pending = AddedToCart.objects.filter(customer=request.user, is_pending=True).aggregate(Sum('quantity'))['quantity__sum']
    context = {'total_pending': total_pending}
    return render(request, 'cart.html', context)



def checkout(request):
    if not request.user.is_authenticated:
        messages.info(request, 'The page you are trying to access is not available. Please log in first.')
        return redirect('login.html')

    my_cart = AddedToCart.objects.filter(customer = request.user.customer, is_pending = True, is_ordered = False).all().order_by('-date_added')
    
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids')

       



        order_id = str(uuid.uuid4())
        order_total = 0

        i = 0
        for product_id in product_ids:
            my_ordered_product = AddedToCart.objects.filter(customer = request.user.customer, cart_id = product_id).first()
            my_ordered_product.is_pending = False
            my_ordered_product.is_selected = True
            my_ordered_product.is_ordered = True
            my_ordered_product.order_id = order_id

            quantity = my_ordered_product.quantity
            price = my_ordered_product.product.product_price
            total = int(quantity) * int(price) 

            my_ordered_product.total_of_items = total

            order_total = order_total + total   
            my_ordered_product.save()
            i = i + 1 

        my_order = Orders.objects.create(customer = request.user.customer,
                                        shop_owner = my_ordered_product.product.stall_owner,
                                        total = order_total,
                                        total_orders = i,
                                        estimated_time = 10,
                                        date_ordered = datetime.datetime.now(),
                                        order_id = order_id
                                        )
        my_order.save()

        messages.info(request, f'Your order has been checked out, with {my_order.order_id} order id and total of {my_order.total}')
        return redirect('orders.html')

    return render (request,'dashboard/checkout.html', {'my_cart' : my_cart})   

def update_profile(request):

    if request.method == 'POST':
        stall_name = request.POST.get('stall_name')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        bday = request.POST.get('bday')
        brgy = request.POST.get('brgy')
        full_address = request.POST.get('full_address')

        try:

            current_user = User.objects.filter(username = request.user.username).first()
            current_customer = Customer.objects.filter(user = current_user).first()
            if current_customer:
                if request.user.is_superuser:
                    Customer.objects.filter(user = current_user).update(stall_name = stall_name, fname = fname, lname = lname, bday = bday, brgy = brgy, full_address = full_address)
                    messages.info(request, 'Your profile has been updated ')
                    return redirect('update_profile.html')
                else:
                    Customer.objects.filter(user = current_user).update(fname = fname, lname = lname, bday = bday, brgy = brgy, full_address = full_address)
                    messages.info(request, 'Your profile has been updated ')
                    return redirect('update_profile.html')


            else:
                if request.user.is_superuser:
                    create_customer = Customer.objects.create(user = request.user,
                                                                stall_name = stall_name,
                                                                fname = fname,
                                                                lname = lname,
                                                                bday = bday,
                                                                brgy = brgy,
                                                                full_address = full_address)
                    create_customer.save()
                    messages.info(request, 'Your profile has been created.')
                    return redirect('update_profile.html')

                else:
                    return redirect('login.html')


        
        except Exception as e:
            print(e)





    return render(request,'about/update_profile.html')  


@csrf_exempt
@login_required
def update_address(request):
    if request.method == 'POST':
        user = request.user
        user.customer.brgy = request.POST.get('method')
        user.customer.delivery_address = request.POST.get('address')
        user.customer.phone_number = request.POST.get('phone_number')
        user.customer.email = request.POST.get('email')
        user.customer.save()
        messages.info(request, 'Information Updated.')
        return render(request,'update_address.html')
    else:
        return render(request, 'update_address.html')


def profile(request):
    return render(request,'dashboard/profile.html')   


def register(request):

    if not request.user.is_authenticated:
        if request.method == 'POST':
            uname = request.POST.get('uname')
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            bday = request.POST.get('bday')
            brgy = request.POST.get('brgy')
            full_address = request.POST.get('full_address')
            phone_number = request.POST.get('phone_number')
            email = request.POST.get('email')
            pass1 = request.POST.get('pass1')
            pass2 = request.POST.get('pass2')

            if pass1 != pass2:
                messages.info(request, 'The password do not match!')
                return render(request, 'authentication/register.html')
            else:
                user_info = User.objects.create(username = uname, email = email, first_name = fname, last_name = lname)
                user_info.set_password(pass1)
                user_info.save()

                customer_info = Customer.objects.create(user = user_info, fname = fname, lname = lname, bday = bday, brgy = brgy, full_address = full_address, phone_number = phone_number, email = email)
                customer_info.save()

                messages.info(request, f' Thank you for signing up {fname} {lname}. Please login.')
                return redirect('login.html')

    else:
        messages.info(request, 'You are currently logged in. Please log out first.')
        return redirect('home.html')
            

    return render(request, 'authentication/register.html')


def log_in(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            email_or_username = request.POST.get('email_or_username')
            password = request.POST.get('password')

            try:
                if '@' in email_or_username:
                    user = User.objects.get(email=email_or_username)
                    if user:
                        user = authenticate(username=user.username, password=password)
                        if user:
                            login(request, user)
                            messages.info(request, f'You are successfully logged in {user.username}')
                            return redirect('home.html')
                        else:
                            messages.info(request, 'The credentials that you have entered is invalid')
                            return redirect('login.html')
                else:
                    user = authenticate(username=email_or_username, password=password)
                    if user:
                        login(request, user)
                        messages.info(request, f'You are successfully logged in {email_or_username}')
                        return redirect('home.html')
                    else:
                        messages.info(request, 'The credentials that you have entered is invalid')
                        return redirect('login.html')
            except User.DoesNotExist:
                messages.info(request, 'The email or username you entered does not exist')
                return redirect('login.html')
    else:
        messages.info(request, 'You are currently logged in. Please log out first.')
        return redirect('home.html')
    return render(request, 'authentication/login.html')

  

def user_logout(request):
    logout(request)
    return redirect('/home.html')

def dashboard(request):
    if request.user.is_superuser == False:
        messages.info(request, 'You must log-in to continue.')
        return redirect('login.html')
    
    total_product = len(ProductList.objects.filter(stall_owner = request.user).all())
                   
    orders_container = []
    all_orders = Orders.objects.filter(shop_owner = request.user).all()

    for order in all_orders:
        if (datetime.datetime.now()).strftime('%B %d %Y') == (order.date_ordered).strftime('%B %d %Y'):
            orders_container.append(order)

    i = 0
    for order_today in orders_container:
        i = i + order_today.total_orders
    
    all_customers = []
    earnings_today = 0
    for order in orders_container:
        if not order.customer.user.username in all_customers:
            all_customers.append(order.customer.user.username)
        earnings_today = earnings_today + order.total


    product_name = [] #labels
    product_sales = [] # data
    
    sales_of_a_product = 0
    for my_product in ProductList.objects.filter(stall_owner = request.user).all():
        product_name.append(my_product.product_id)
        for ordered_items in orders_container:
            for added_to_cart in AddedToCart.objects.filter(order_id = ordered_items.order_id, product = my_product).all():
                sales_of_a_product = sales_of_a_product + added_to_cart.total_of_items
        
        product_sales.append(sales_of_a_product)
        sales_of_a_product = 0
                
    messages.info(request, f'{product_name}')
    messages.info(request, f'{product_sales}')

    context = {'total_customer': len(all_customers),
                'total_order': i,
                'total_product': total_product,
                'earnings_today' : earnings_today,
                'product_names' : dumps(product_name),
                'product_sales' : dumps(product_sales),
                'name_legend' : product_name}

    return render(request, 'admin/dashboard.html', context)


def report_generator(request):
    if request.user.is_superuser == False:
        messages.info(request, 'The page you are trying to access is not available.')
        return redirect('/home.html')
    
    logo = Logo.objects.filter().first()
    

    

    orders_list = []

    for orders in Orders.objects.filter(shop_owner = request.user).all():
        for added_to_cart in AddedToCart.objects.filter(order_id = orders.order_id).all():
            orders_list.append(added_to_cart)



    template_path = 'reports/report.html'
    context = {'user': request.user, 'logo' : logo, 'orders_list' : orders_list}

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="food_hub_report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)
    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response






def chart(request):
    return render(request,'admin/chart.html')        

def calendar(request):
    return render(request,'admin/calendar.html')


def download_excel(request):

    title = 'Foodhub Product List'

    buffer = io.BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet()

    date_today = (datetime.datetime.now()).strftime('%B %d %Y')

    product_list = ProductList.objects.filter().all()

    worksheet.write('A1', 'Product list with corresponding available stocks')
    worksheet.write('A2', f'as of : {date_today}')


    worksheet.write('A5', 'Stall Owner')
    worksheet.write('B5', 'Product Id')
    worksheet.write('C5', 'Product Name')
    worksheet.write('D5', 'Product Price')
    worksheet.write('E5', 'Stocks')

    i = 6
    for product in product_list:
        worksheet.write(f'A{i}', product.stall_owner.customer.fname)
        worksheet.write(f'B{i}', product.product_id)
        worksheet.write(f'C{i}', product.product_name)
        worksheet.write(f'D{i}', product.product_price)
        worksheet.write(f'E{i}', product.stocks)
        i = i + 1

    workbook.close()
    buffer.seek(0)

    return FileResponse(buffer, as_attachment= True, filename=f'{title}.xlsx')


def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password == confirm_password:
            user = request.user
            if user.check_password(current_password):
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password has been changed successfully.')
                return redirect("/")
            else:
                messages.error(request, "Please enter valid current password.")
                return render(request, "change_password.html")
        else:
            messages.error(request, "You must enter the same password twice in order to proceed, Please try again.")
            return render(request, "change_password.html")
    else:
        return render(request, "change_password.html")


    
