from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Connexion réussie !")
            return redirect(index)  # Redirigé vers la page daccueil après connexion
        else:
            messages.error(request, "Identifiants incorrects.")

    return render(request,'index.html')



def index(request):
    return render(request, 'index.html')


def tabpersonels(requests):
    return render(requests, 'data_personels.html')