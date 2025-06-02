from django.shortcuts import render
from django.contrib.auth import logout

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.urls import reverse_lazy
from Geequipe.models import ChefProjet


def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Vérifie si cet utilisateur est un chef de projet
            if ChefProjet.objects.filter(user=user).exists():
                login(request, user)
                messages.success(request, "Connexion réussie en tant que Chef de Projet !")
                return redirect('index')  # Redirige vers la page d'accueil
            else:
                messages.error(request, "Accès réservé aux Chefs de Projet.")
        else:
            messages.error(request, "Identifiants incorrects.")

    return render(request, 'login.html')




def index(request):
    return render(request, 'index.html')


def tabpersonels(requests):
    return render(requests, 'data_personels.html')


def tabprojet(requests):
    return render(requests, 'projet.html')









def logout_view(request):
    return redirect('login')
    
