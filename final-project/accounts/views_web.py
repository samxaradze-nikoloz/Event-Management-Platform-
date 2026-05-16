from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            login(request, user)
            return redirect('/events/')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email    = request.POST['email']
        password = request.POST['password']
        role     = request.POST.get('role', 'attendee')
        bio      = request.POST.get('bio', '')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        else:
            user = User.objects.create_user(
                username=username, email=email,
                password=password, role=role, bio=bio
            )
            login(request, user)
            return redirect('/events/')
    return render(request, 'accounts/register.html')

def logout_view(request):
    logout(request)
    return redirect('/accounts/login/')

def me_view(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    return render(request, 'accounts/me.html', {'user': request.user})