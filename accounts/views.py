from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, auth
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


# Create your views here.
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.info(request, 'Please enter both username and password.')
            return redirect('login')

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'invalid credentials')
            return redirect('login')
    else:    
         return render(request, 'login.html')

def signup(request):

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not email or not password:
            messages.info(request, 'Please fill in all required fields.')
            return redirect('signup')

        if password != confirm_password:
            messages.info(request, 'password not matching...')
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.info(request, 'Username Taken')
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.info(request, 'Email in use')
            return redirect('signup')

        try:
            validate_password(password)
        except ValidationError as e:
            messages.info(request, ' '.join(e.messages))
            return redirect('signup')

        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password,
        )
        new_user = authenticate(username=username, password=password)
        if new_user is not None:
            login(request, new_user)
            messages.success(request, 'Signup successful. You are now logged in.')
            return redirect('profile_setup')
        else:
            messages.error(request, 'Something went wrong. Please try logging in.')
            return redirect('login')

    else:   
        return render(request, 'signup.html')


def logout(request):
    auth.logout(request)
    return redirect('/')