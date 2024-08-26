from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

def login_required_with_message(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect(reverse('login'))
    return wrapper
