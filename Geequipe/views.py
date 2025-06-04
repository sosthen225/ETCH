from urllib import request
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from Geequipe.models import ChefProjet, Projet , Client
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from Geequipe.models import ChefProjet, Projet, Client

import json
from datetime import datetime


@csrf_protect
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


# def tabprojet(requests):
#     projets = Projet.objects.all()
#     return render(requests, 'projet.html', {'projets': projets})


def tabprojet(requests):
    projets = Projet.objects.all()
    chefs_de_projet = User.objects.all()
    clients = Client.objects.all()
    return render(requests, 'projet.html', {
        'projets': projets,
        'chefs_de_projet': chefs_de_projet,
        'clients': clients,
    })





# @csrf_exempt
# def ajouter_projet(request):
#     if request.method == "POST":
#         data = json.loads(request.body)

#         try:
#             chef_projet = ChefProjet.objects.get(nom=data["chef_projet"])
#             client = Client.objects.get(nom=data["client"])
#         except (ChefProjet.DoesNotExist, Client.DoesNotExist):
#             return JsonResponse({"success": False, "message": "Chef de projet ou client introuvable"}, status=400)

#         projet = Projet.objects.create(
#             nom=data["nom_projet"],
#             type=data["type"],
#             date_debut=datetime.strptime(data["date_debut"], "%Y-%m-%d").date(),
#             date_fin=datetime.strptime(data["date_fin"], "%Y-%m-%d").date(),
#             site=data["site"],
#             ville=data["ville"],
#             pays=data["pays"],
#             chef_projet=chef_projet,
#             client=client
#         )
        

#         return JsonResponse({"success": True, "message": "Projet ajouté"})
#     return JsonResponse({"success": False, "message": "Méthode non autorisée"}, status=405)



from django.http import JsonResponse
from .models import Projet, Client
from django.contrib.auth import get_user_model

User = get_user_model()
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Projet, Client, ChefProjet
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST 
from django.db import transaction

@csrf_exempt

@csrf_exempt
def ajouter_projet(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        nom = data.get('nom')
        type_ = data.get('type')
        date_debut = data.get('date_debut')
        date_fin = data.get('date_fin')
        site = data.get('site')
        ville = data.get('ville')
        pays = data.get('pays')
        statut = data.get('statut')
        chef_projet_id = data.get('chef_projet')
        client_nom = data.get('client_nom').strip()

        # ✅ 1. Cherche le client existant ou crée-le
        client = Client.objects.filter(nom__iexact=client_nom).first()
        if not client:
            client = Client.objects.create(nom=client_nom)

        # ✅ 2. Récupère le chef de projet
        chef_projet = ChefProjet.objects.get(id=chef_projet_id)

        # ✅ 3. Crée le projet
        Projet.objects.create(
            nom=nom,
            type=type_,
            date_debut=date_debut,
            date_fin=date_fin,
            site=site,
            ville=ville,
            pays=pays,
            statut=statut,
            chef_projet=chef_projet,
            client=client
        )

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

   



def logout_view(request):
    return redirect('login')
    
