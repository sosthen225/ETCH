from urllib import request
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

from Geequipe.models import ChefProjet, Projet, Client

import json
from datetime import datetime



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


@csrf_exempt
def ajouter_projet(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            nom = data.get('nom')
            type_proj = data.get('type')
            date_debut = data.get('date_debut')
            date_fin = data.get('date_fin')
            site = data.get('site')
            ville = data.get('ville')
            pays = data.get('pays')
            statut = data.get('statut')
            chef_projet_id = data.get('chef_projet')
            client_id = data.get('client_id')
            nouveau_client_nom = data.get('nouveau_client', '').strip()

            if not nom or not chef_projet_id or not statut:
                return JsonResponse({'success': False, 'error': 'Champs obligatoires manquants.'})

            # Récupérer ou créer client
            if client_id == 'autre':
                if not nouveau_client_nom:
                    return JsonResponse({'success': False, 'error': 'Le nom du nouveau client est requis.'})
                # Vérifie si le client existe déjà (optionnel)
                client, created = Client.objects.get_or_create(nom=nouveau_client_nom)
            else:
                client = get_object_or_404(Client, id=client_id)

            chef_projet = get_object_or_404(User, id=chef_projet_id)

            projet = Projet.objects.create(
                nom=nom,
                type=type_proj,
                date_debut=date_debut,
                date_fin=date_fin,
                site=site,
                ville=ville,
                pays=pays,
                statut=statut,
                chef_projet=chef_projet,
                client=client,
            )

            return JsonResponse({'success': True, 'id': projet.id})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Méthode non autorisée.'})

   



def logout_view(request):
    return redirect('login')
    
