from .serializers import UserSerializer, CategoryTypeSerializer, CategoryItemSerializer, OrderSerializer, StatusSerializer, OrderItemSerializer
from .models import CategoryItem, CategoryType, User, Order, Status, OrderItem
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.middleware.csrf import get_token
from django.http import HttpResponse, JsonResponse
from stripe.error import StripeError
from django.contrib import messages
from rest_framework import viewsets
from django.conf import settings
from dateutil import parser
import requests
import stripe
import shutil
import uuid
import os

# Create your views here.
    
def signin(request):
    if request.session.session_key:
        user = get_object_or_404(User, session_id=request.session.session_key)
        return redirect('homepage', user.username)

    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            try:
                user = User.objects.get(username=username, password=password)
                if user.is_signed_in:       
                    return JsonResponse({'error_message': 'You are already signed in on another browser.'})
                else:
                    if not request.session.session_key:
                        request.session.save()
                    session_key = request.session.session_key
                    user.sign_in(session_key)
                    return JsonResponse({'username': user.username})
            except User.DoesNotExist:
                return JsonResponse({'error_message': 'Invalid username or password.'})

    return render(request, 'signin.html')

def signout(request, username):
    try:
        user = get_object_or_404(User, username=username)
        if request.session.session_key == user.session_id:
            user.sign_out()
            request.session.flush()
            return redirect('signin')
        else:
            return JsonResponse(request, 'You are not signed in on this browser.')
    except User.DoesNotExist:
        return JsonResponse(request, 'Invalid employee ID.')

def localhost(request):
    return redirect('homepage', 'username')

def createCart(username):
    customer = get_object_or_404(User, username=username)
    status = get_object_or_404(Status, name='waiting')
    order = Order.objects.create(customer=customer, status=status)
    return order

def getOrders(username, status_range):
    n, m = status_range
    customer = getResponse('users', 'username', username)
    status_lst = [sta['id'] for sta in getResponse('status', '', '') if sta['id'] > n and sta['id'] < m]
    orders = [order for order in getResponse('orders', 'customer_id', str(customer[0]['id'])) if order['status']['id'] in status_lst]
    return orders

def getOrderObject(username, status_range):
    n, m = status_range
    customer = get_object_or_404(User, username=username)
    status_lst = [sta for sta in Status.objects.all() if sta.id > n and sta.id < m]
    orders = [order for order in Order.objects.all().filter(customer=customer) if order.status in status_lst]
    if orders != []:
        order = orders[0]  
        return order

def getOrder(username):
    orders = getOrders(username, (0, 2))
    if orders != []:
        order = orders[0]  
        return order
    
def renderContext(user, range):
    n, m, l = range
    types = ', '.join([type.name for type in CategoryType.objects.all()])
    status = [status for status in Status.objects.all() if status.id > n and status.id < m]
    items = [item for item in OrderItem.objects.all() if item.order.status.id >= l and item.order.status.id < 11]
    if user.role == 'supplier':
        categories = CategoryItem.objects.all().filter(supplier=user)
        items = [item for item in items if item.category in categories]
    orders = [order for order in Order.objects.all() if order.id in list(dict.fromkeys([item.order.id for item in items]))] 
    context = {
        'user': user,
        'status': status,
        'orders': orders,
        'items': items,
        'types': types,
        'nOo': len(orders),
    }
    return context

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.all().order_by('id')
        username = self.request.query_params.get('username')
        password = self.request.query_params.get('password') 

        if username is not None and password is not None:
            queryset = queryset.filter(username=username, password=password)
        elif username is not None:
            queryset = queryset.filter(username=username)

        return queryset
    
class CategoryTypeViewSet(viewsets.ModelViewSet):
    serializer_class = CategoryTypeSerializer

    def get_queryset(self):
        queryset = CategoryType.objects.all().order_by('id')
        name = self.request.query_params.get('name')
        if name is not None:
            queryset = queryset.filter(name=name)

        return queryset
    
class CategoryItemViewSet(viewsets.ModelViewSet):
    serializer_class = CategoryItemSerializer

    def get_queryset(self):
        queryset = CategoryItem.objects.all().order_by('id')
        id = self.request.query_params.get('id')
        is_available = self.request.query_params.get('is_available')
        is_new = self.request.query_params.get('is_new')
        if id is not None:
            queryset = queryset.filter(id=id)
        elif is_new is not None and is_available is not None:
            queryset = queryset.filter(is_available=is_available, is_new=is_new)
        elif is_available is not None:
            queryset = queryset.filter(is_available=is_available)
        elif is_new is not None:
            queryset = queryset.filter(is_new=is_new)

        return queryset

class StatusViewSet(viewsets.ModelViewSet):
    serializer_class = StatusSerializer

    def get_queryset(self):
        queryset = Status.objects.all().order_by('id')
        name = self.request.query_params.get('name')
        if name is not None:
            queryset = queryset.filter(name=name)

        return queryset
    
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.all().order_by('id')
        customer_id = self.request.query_params.get('customer_id')
        status_id = self.request.query_params.get('status_id')

        if customer_id is not None and status_id is not None:
            queryset = queryset.filter(customer_id=customer_id, status_id=status_id)
        elif customer_id is not None:
            queryset = queryset.filter(customer_id=customer_id)
        elif status_id is not None:
            queryset = queryset.filter(status_id=status_id)

        return queryset
    
class OrderItemViewSet(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        queryset = OrderItem.objects.all().order_by('id')
        order_id = self.request.query_params.get('order_id')
        if order_id is not None:
            queryset = queryset.filter(order_id=order_id)

        return queryset
    
def getResponse(path, query, param):
    query = query.split(', ')
    if len(query) <= 1:
        reponse = requests.get(f'http://127.0.0.1:8000/api/'+path+'/?'+query[0]+'='+param).json()
    else:
        reponse = requests.get(f'http://127.0.0.1:8000/api/'+path+'/?'+query[0]+'='+param[0]+'&'+query[1]+'='+param[1]).json()
    return reponse

def homepage(request, username):
    
    if username == 'username':
        return redirect('signin')
    else:
        user = getResponse('users', 'username', username)

        if not user[0]['is_signed_in'] or request.session.session_key != user[0]['session_id']:
            return redirect('signin')
    
    if user[0]['role'] == 'customer':

        types = getResponse('categorytypes', '', '')
        items = getResponse('categoryitems', 'is_available, is_new', ['True', 'False'])
        status = getResponse('status', 'name', 'waiting')
        order = getResponse('orders', 'customer_id, status_id', [str(user[0]['id']), str(status[0]['id'])])

        context = {
            'user': user,
            'types': types,
            'items': items,
            'type': types[0]
        }

        if order != []:
            order_items = getResponse('orderitems', 'order_id', str(order[0]['id']))
            context.update({'len': len(order_items), 'order': order})
        else:
            context.update({'len': 0})

        if request.method == 'POST':
            type_name = request.POST['type']
            current_type = getResponse('categorytypes', 'name', type_name)
            content = request.POST['content']
            new_items = [item for item in items if item['type']==current_type[0] and item['name'].lower().startswith(content.lower())]
            context.update({'items': new_items, 'type': current_type[0]})
            if new_items == []:
                context.update({'message': 'No product match your searchs'})
                        
        return render(request, 'index.html', context)
    
    elif user[0]['role'] == 'admin':
        user = get_object_or_404(User, username=username)
        supplier_view(request, username, '6, 10, 6')
        context = renderContext(user, (6, 10, 6))
        context.update({'csrf_token': get_token(request), 'range': '6, 10, 6'})

        return render(request, 'admin.html', context)
    
    else:
        user = get_object_or_404(User, username=username)
        supplier_view(request, username, '3, 7, 3')
        context = renderContext(user, (3, 7, 3))
        context.update({'csrf_token': get_token(request), 'range': '3, 7, 3'})

        if request.method == 'POST':
            name = request.POST['name']
            ingredient = request.POST['ingredient']
            indication = request.POST['indication']
            contraindication = request.POST['contraindication']
            dosage = request.POST['dosage']
            side_effects = request.POST['side_effects']
            carefull = request.POST['carefull']
            drug_interactions = request.POST['drug_interactions']
            preserve = request.POST['preserve']
            type_name = request.POST['type']
            price = request.POST['price']
            quantity = request.POST['quantity']
            image = request.FILES.get('picture')
            if image is not None and image.name.endswith('.jpg'):
                filename = str(uuid.uuid4()) + '.jpg'
                filepath = os.path.join(settings.STATIC_ROOT, 'images', filename)
                with open(filepath, 'wb+') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)
                shutil.copy(filepath, str(settings.BASE_DIR) + '\order_management\static\images')

                category_type = get_object_or_404(CategoryType, name=type_name)
                category_item = CategoryItem.objects.create(name=name, type=category_type, supplier=user, ingredient=ingredient, indication=indication, contraindication=contraindication, dosage=dosage, side_effects=side_effects, carefull=carefull, drug_interactions=drug_interactions, preserve=preserve, price=price, photo=filename)
                if quantity != '':
                    category_item.quantity = quantity    
                    category_item.save()

                context.update({'message': 'Add successful!'})

            else:

                context.update({'message': 'Add failed!'})

        return render(request, 'supplier.html', context)
    
def manager(request, username):
    user = get_object_or_404(User, username=username)

    if not user.is_signed_in or request.session.session_key != user.session_id:
        return redirect('signin')
    
    content = '<div class="container-fluid"></div><div class="row" style="padding: 30px"><div class="form_container"><form id="supply-form" method="post" enctype="multipart/form-data"><div class="row"><div class="col-100"><h3 style="padding:20px 0px 10px 0px">Add Product</h3><label for="name">Name</label><input type="text" id="name" name="name" required/><label for="ingredient">Ingredient</label><input type="text" id="ingredient" name="ingredient" required/><label for="indication">Indication</label><input type="text" id="indication" name="indication" required/><label for="contraindication">Contraindication</label><input type="text" id="contraindication" name="contraindication" required/><label for="dosage">Dosage</label><input type="text" id="dosage" name="dosage" required/><label for="side_effects">Side effects</label><input type="text" id="side_effects" name="side_effects" required/><label for="carefull">Carefull</label><input type="text" id="carefull" name="carefull" required/><label for="drug_interactions">Drug interactions</label><input type="text" id="drug_interactions" name="drug_interactions" required/><label for="preserve">Preserve</label><input type="text" id="preserve" name="preserve" required/><label for="desc"><label for="type">Type</label><select id="type" name="type"></select><label for="picture">Picture</label><input type="file" id="picture" name="picture"/><div class="row"><div class="col-50"><label for="price">Price</label><input type="number" id="price" name="price" required/></div><div class="col-50"><label for="quantity">Quantity</label><input type="number" id="quantity" name="quantity"/></div></div></div></div><input type="submit" value="Add Product" class="add_btn"/></form></div></div></div>'
    return HttpResponse(content)
    
def supplier_add(request, username):
    user = get_object_or_404(User, username=username)

    if not user.is_signed_in or request.session.session_key != user.session_id:
        return redirect('signin')

    content = '<div class="container-fluid"></div><div class="row" style="padding: 30px"><div class="form_container"><form id="supply-form" method="post" enctype="multipart/form-data"><div class="row"><div class="col-100"><h3 style="padding:20px 0px 10px 0px">Add Product</h3><label for="name">Name</label><input type="text" id="name" name="name" required/><label for="ingredient">Ingredient</label><input type="text" id="ingredient" name="ingredient" required/><label for="indication">Indication</label><input type="text" id="indication" name="indication" required/><label for="contraindication">Contraindication</label><input type="text" id="contraindication" name="contraindication" required/><label for="dosage">Dosage</label><input type="text" id="dosage" name="dosage" required/><label for="side_effects">Side effects</label><input type="text" id="side_effects" name="side_effects" required/><label for="carefull">Carefull</label><input type="text" id="carefull" name="carefull" required/><label for="drug_interactions">Drug interactions</label><input type="text" id="drug_interactions" name="drug_interactions" required/><label for="preserve">Preserve</label><input type="text" id="preserve" name="preserve" required/><label for="desc"><label for="type">Type</label><select id="type" name="type"></select><label for="picture">Picture</label><input type="file" id="picture" name="picture"/><div class="row"><div class="col-50"><label for="price">Price</label><input type="number" id="price" name="price" required/></div><div class="col-50"><label for="quantity">Quantity</label><input type="number" id="quantity" name="quantity"/></div></div></div></div><input type="submit" value="Add Product" class="add_btn"/></form></div></div></div>'
    return HttpResponse(content)

def supplier_view(request, username, range):
    user = get_object_or_404(User, username=username)

    if not user.is_signed_in or request.session.session_key != user.session_id:
        return redirect('signin')
    
    context = renderContext(user, [int(ran) for ran in range.split(', ')])
    content = render_to_string('supplier-dashboard.html', context)
    return HttpResponse(content)

def accept(request, username, order_id, status_id):
    user = get_object_or_404(User, username=username)

    if not user.is_signed_in or request.session.session_key != user.session_id:
        return redirect('signin')
    
    new_status = get_object_or_404(Status, id=status_id)
    order = get_object_or_404(Order, id=order_id)
    if new_status.id > 6 and new_status.id < 11:
        items = OrderItem.objects.all().filter(order=order)
        for item in items:
            item.category.quantity -= item.quantity
            if item.category.quantity == 0:
                item.category.is_available = False
                for it in OrderItem.objects.all().filter(category=item.category):
                    if it.order != item.order and len([i for i in OrderItem.objects.all().filter(order=it.order)]) == 1 and it.order.status.id < 6:
                        denied_status = get_object_or_404(Status, name='denied')
                        it.order.status = denied_status
                        it.order.save()
            item.category.save()
    order.status = new_status
    order.save()

    return redirect('homepage', username)

def profile(request, username):
    user = getResponse('users', 'username', username)

    if not user[0]['is_signed_in'] or request.session.session_key != user[0]['session_id']:
        return redirect('signin')
    
    if request.method == 'POST':
        name = request.POST['name']
        phone = request.POST['phone']
        address = request.POST['address']
        zip = request.POST['zip']
        o_pass = request.POST['o-pass']
        n_pass = request.POST['n-pass']

        if o_pass == user[0]['password']:
            user_object = get_object_or_404(User, username=username)
            user_object.name = name
            user_object.phone = phone
            user_object.address = address
            user_object.zip = zip
            if len(n_pass) > 0:
                if len(n_pass) > 6:
                    user_object.password = n_pass
                else:
                    return JsonResponse({'error_message': 'Password must be more than 6 characters length!'})
            
            user_object.save()
            return JsonResponse({'success_message': 'Update successful!'})
        else:
            return JsonResponse({'error_message': 'Invalid password!'})

    types = getResponse('categorytypes', '', '')
    context = {
        'sign_in_time': parser.parse(user[0]['sign_in_time']).strftime("%B %d, %Y, %I:%M %p"),
        'user': user,
        'types': types,
        'len': 0,  
    }
    order = getOrder(username)
    if order != None:
        order_items = getResponse('orderitems', 'order_id', str(order['id']))
        context.update({'len': len(order_items)})

    orders = getOrders(username, (1, 11)) 
    if len(orders) != 0:
        context.update({'nearest_order_time': parser.parse(orders[len(orders)-1]['order_time']).strftime("%B %d, %Y, %I:%M %p"), 'sum': sum([float(order['total_cost']) for order in orders])})
        
    return render(request, 'profile.html', context)

def product(request, username, item_id):
    item = getResponse('categoryitems', 'id', str(item_id))
    user = getResponse('users', 'username', username)

    if not user[0]['is_signed_in'] or request.session.session_key != user[0]['session_id']:
        return redirect('signin')
    
    if request.method == 'POST':
        quantity = request.POST['quantity']
        return redirect('additem', username, item_id, quantity)
    
    types = getResponse('categorytypes', '', '')

    context = {
        'item': item,
        'types': types,
        'user': user,
        'len': 0,
    }

    order = getOrder(username)
    
    if order != None:
        context.update({'len': len(getResponse('orderitems', 'order_id', str(order['id'])))})
        
    return render(request, 'product.html', context)

def additem(request, username, item_id, quantity):
    user = getResponse('users', 'username', username)

    if not user[0]['is_signed_in'] or request.session.session_key != user[0]['session_id']:
        return redirect('signin')

    order = getOrderObject(username, (0, 2))
    if order == None:
        order = createCart(username)

    category = get_object_or_404(CategoryItem, id=item_id)

    try:
        item = OrderItem.objects.get(order=order, category=category)
        item.quantity += quantity
    except OrderItem.DoesNotExist:
        item = OrderItem.objects.create(order=order, category=category, quantity=quantity) 

    item.get_subtotal_cost()
    item.save()

    return redirect('homepage', username)

def updateitem(request, username, item_id, quantity):
    user = getResponse('users', 'username', username)

    if not user[0]['is_signed_in'] or request.session.session_key != user[0]['session_id']:
        return redirect('signin')

    item = get_object_or_404(OrderItem, id=item_id)
    item.quantity = quantity
    item.get_subtotal_cost()
    item.save()

    return redirect('cart', username)

def deleteitem(request, username, item_id):
    user = getResponse('users', 'username', username)

    if not user[0]['is_signed_in'] or request.session.session_key != user[0]['session_id']:
        return redirect('signin')

    item = get_object_or_404(OrderItem, id=item_id)
    item.delete()

    order = getOrderObject(username, (0, 2))
    items = getResponse('orderitems', 'order_id', str(order.id))
    if len(items) == 0:
        order.delete()

    return redirect('cart', username)

def deleteorder(request, username):
    user = getResponse('users', 'username', username)

    if not user[0]['is_signed_in'] or request.session.session_key != user[0]['session_id']:
        return redirect('signin')

    order = getOrderObject(username, (0, 2))
    order.delete()

    return redirect('cart', username)

def cart(request, username):
    user = getResponse('users', 'username', username)

    if not user[0]['is_signed_in'] or request.session.session_key != user[0]['session_id']:
        return redirect('signin')
    
    types = getResponse('categorytypes', '', '')

    context = {
        'user': user,
        'types': types,
        'len': 0,
    }

    order = getOrderObject(username, (0, 2))

    if order != None:
        order.get_total_cost()
        order.save()
        items = getResponse('orderitems', 'order_id', str(order.id))
        context.update({'len': len(items), 'order': order, 'items': items})

    return render(request, 'cart.html', context)

def payment(request, username):
    user = getResponse('users', 'username', username)

    if not user[0]['is_signed_in'] or request.session.session_key != user[0]['session_id']:
        return redirect('signin')
    
    order = getOrderObject(username, (0, 2))
    status = Status.objects.get(name='forwarded')
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        address = request.POST['address'] + '(' + request.POST['state'] + ')'
        phone = request.POST['phone']
        zip = request.POST['zip']
        
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            charge = stripe.Charge.create(
                amount = int(order.total_cost)*100,
                currency = 'usd',
                source = request.POST['stripeToken'],
                description = 'Charge for ' + username + ' order'
            )
            user_object = get_object_or_404(User, username=username)
            user_object.name = name
            user_object.email = email
            user_object.address = address
            user_object.phone = phone
            user_object.zip = zip
            user_object.save()
            order.status = status
            order.save()
            
            return redirect('cart', username)

        except StripeError as e:
            messages.error(request, str(e).split(':')[1])

    types = getResponse('categorytypes', '', '')
    items = getResponse('orderitems', 'order_id', str(order.id))
    context = {
        'user': user,
        'len': len(items),
        'items': items,
        'order': order,
        'types': types,
        'publishable_key': settings.STRIPE_PUBLISHABLE_KEY
    }

    return render(request, 'payment.html', context)