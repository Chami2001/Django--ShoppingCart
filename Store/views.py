from django.shortcuts import render,redirect
from .models import *
from django.http import JsonResponse
import json
import datetime
from .utils import cookieCart, cartData, guestOrder


# for userCreation
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib import messages

# authenticate user
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def registerUser(request):
    form = CreateUserForm()

    if request.method=="POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')

            Customer.objects.create(username=User.objects.get(username=user), email=email)
            return redirect('login')

    context={'form':form}
    return render(request, 'store/register.html',context)

def loginUser(request):
    if request.method =="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('store')
        else:
            messages.info(request, 'Incorrect username or password')
    context={}
    return render(request, 'store/login.html',context)

def logoutUser(request):
    logout(request)
    return redirect('store')


def store(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context ={'products':products, 'cartItems':cartItems}
    return render(request, 'store/store.html',context)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context ={'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/cart.html',context)

def checkout(request):
    
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
        
    context ={'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/checkout.html',context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action:',action)
    print('productId:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer = customer, cart_complete = False)

    order_item, created= Order_Item.objects.get_or_create(order = order, product= product)

    if action == 'add':
        order_item.quantity = (order_item.quantity + 1)
    elif action == 'remove':
        order_item.quantity = (order_item.quantity - 1)    

    order_item.save()

    if order_item.quantity <=0:
        order_item.delete()

    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer, cart_complete = False)
        


    else:
        customer, order = guestOrder(request, data)


    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_total_price:
        order.cart_complete = True
    order.save()

    if order.shipping == True:
         ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            pincode=data['shipping']['pincode'],
        )

    return JsonResponse('Payment complete', safe=False)
