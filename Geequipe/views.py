from urllib import request
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from Geequipe.forms import ProjetForm
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
from django.utils.dateparse import parse_date









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



def tabprojet(requests):
    projets = Projet.objects.all()
    chefs_de_projet = User.objects.all()
    clients = Client.objects.all()
    return render(requests, 'projet.html', {
        'projets': projets,
        'chefs_de_projet': chefs_de_projet,
        'clients': clients,
    })




User = get_user_model()
@csrf_exempt
def ajouter_projet(request):
    if request.method == 'POST':
        try:
            print("Début ajout projet")
            data = json.loads(request.body)
            print("Données reçues:", data)

            client_nom = data.get('client_nom', '').strip()
            client, _ = Client.objects.get_or_create(nom=client_nom)
            print(f"Client récupéré/créé : {client}")

            user = User.objects.get(id=int(data.get('chef_projet')))
            chef_projet = ChefProjet.objects.get(user=user)
            print(f"Chef de projet récupéré : {chef_projet}")

            projet = Projet(
                nom=data.get('nom'),
                type=data.get('type'),
                date_debut=data.get('date_debut'),
                date_fin=data.get('date_fin'),
                site=data.get('site'),
                ville=data.get('ville'),
                pays=data.get('pays'),
                statut=data.get('statut'),
                client=client,
                chef_projet=chef_projet
            )

            # Validation personnalisée
            projet.clean()

            # Sauvegarde après validation
            projet.save()
            print("Projet créé avec succès")

            return JsonResponse({'success': True})

        except ValidationError as ve:
            print("Erreur de validation :", ve.message)
            return JsonResponse({'success': False, 'error': ve.message}, status=400)
            
        except User.DoesNotExist:
            print("Erreur : Utilisateur introuvable")
            return JsonResponse({'success': False, 'error': 'Utilisateur introuvable'}, status=400)
        except ChefProjet.DoesNotExist:
            print("Erreur : Chef de projet introuvable")
            return JsonResponse({'success': False, 'error': 'Chef de projet introuvable'}, status=400)
        except Exception as e:
            print("Erreur dans ajouter_projet:", e)
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    print("Erreur : Méthode non autorisée")
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)




@csrf_exempt

def modifier_projet(request,id):
    projet = get_object_or_404(Projet, id=id)
    if request.method == 'POST':
        form = ProjetForm(request.POST, instance=projet)
        if form.is_valid():
            form.save()
            return redirect('tabprojet')
    else:
        form = ProjetForm(instance=projet)
    return render(request, 'modifier_projet.html', {'form': form})




def supprimer_projet(request, id):
    projet = get_object_or_404(Projet, id=id)
    if request.method == 'POST':
        projet.delete()
    return redirect('tabprojet')







from django.forms.models import model_to_dict

def projet_json(request, projet_id):
    projet = get_object_or_404(Projet, id=projet_id)
    data = model_to_dict(projet)
    # Adapter les données si besoin, par exemple retourner l'id du chef de projet et le nom client séparément
    data['chef_projet_id'] = projet.chef_projet.id
    data['client_nom'] = projet.client.nom
    return JsonResponse(data)








def liste_personnel(request):
    agents = Agent.objects.all().prefetch_related('competences', 'certificats')
    return render(request, 'personnel/liste.html', {'agents': agents})

def get_competences_certificats(request):
    if request.method == "GET":
        competences = list(Competence.objects.values('id', 'nom'))
        certificats = list(Certificat.objects.values('id', 'intitule'))
        return JsonResponse({'competences': competences, 'certificats': certificats})
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

@require_http_methods(["POST"])
def enregistrer_agent(request):
    try:
        data = json.loads(request.body)

        agent = Agent.objects.create(
            nom=data['nom'],
            prenoms=data['prenoms'],
            email=data['email'],
            telephone=data['telephone'],
            nationalite=data['nationalite'],
            statut=data['statut'],
            residence=data['residence'],
            pays_affectation=data['pays_affectation'],
        )

        # Associer les compétences
        if 'competences' in data:
            agent.competences.set(data['competences'])

        # Ajouter les certificats
        for cert in data.get('certificats', []):
            Certificat.objects.create(
                agent=agent,
                intitule=cert['intitule'],
                date_obtention=cert['date_obtention']
            )

        return JsonResponse({'message': 'Agent enregistré avec succès', 'agent_id': agent.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)








def logout_view(request):
    return redirect('login')
    
