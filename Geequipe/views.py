from urllib import request
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from Geequipe.forms import EquipeForm, MembreFormSet, ModifierPersonnelForm, ProjetForm
from Geequipe.models import ChefProjet, Projet , Client
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import date, datetime, timedelta, timezone
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
from .models import COMPETENCE_CHOICES, PAYS_CHOICES, Certificat, Competence, Equipe, Expatriation, Membre, PaysAffectation, Personnel, Projet, Client, Posseder
from django.contrib.auth import get_user_model
User = get_user_model()
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Projet, Client, ChefProjet
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST 
from django.utils.dateparse import parse_date
from django.core.files.uploadedfile import UploadedFile
from django.shortcuts import render, redirect
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils.dateparse import parse_date






@csrf_exempt
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
    total_teams = Equipe.objects.count()
    total_personnel = Personnel.objects.count()
    completed_projects = Projet.objects.filter(statut='terminé').count()
    ongoing_projects = Projet.objects.filter(statut='en cours').count()
    completed_projects_list = Projet.objects.filter(statut='terminé').order_by('-date_fin')[:5] # Obtenir les 5 derniers projets terminés

    # Pour les notifications : Projets se terminant bientôt (par exemple, dans les 30 jours)
    today = date.today()
    one_month_from_now = today + timedelta(days=30)
    upcoming_projects = Projet.objects.filter(
    date_fin__gt=today,
    date_fin__lte=one_month_from_now,
    statut='en cours'
).order_by('date_fin')

    # Pour les notifications : Certifications du personnel expirant bientôt (par exemple, dans les 30 jours)
    expiring_personnel = Personnel.objects.filter(
        certification_expiry_date__gt=today,
        certification_expiry_date__lte=one_month_from_now
    ).order_by('certification_expiry_date')


    context = {
        'total_teams': total_teams,
        'ongoing_projects': ongoing_projects,
        'completed_projects': completed_projects,
        'total_personnel': total_personnel,
        'completed_projects_list': completed_projects_list,
        'upcoming_projects': upcoming_projects,
        'expiring_personnel': expiring_personnel,
    }
    return render(request, 'index.html',context)




def tabpersonels(request):
    agents = Personnel.objects.all()
    return render(request, 'data_personels.html',{ 'competences': COMPETENCE_CHOICES,
        'agents': agents,
        'pays_liste':  PAYS_CHOICES,
        'certificats': Certificat.objects.all(),})



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
    # exemple retourner l'id du chef de projet et le nom client séparément
    data['chef_projet_id'] = projet.chef_projet.id
    data['client_nom'] = projet.client.nom
    return JsonResponse(data)










def get_competences_certificats(request):
    if request.method == "GET":
        competences = list(Competence.objects.values('id', 'nom'))
        certificats = list(Certificat.objects.values('id', 'intitule'))
        return JsonResponse({'competences': competences, 'certificats': certificats})
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)




def voir_certificats(request, personnel_id):
    agent = get_object_or_404(Personnel, id=personnel_id)
    certificats = agent.certificats.all()
    return render(request, 'certificats_details.html', {'agent': agent, 'certificats': certificats})





@csrf_exempt
@transaction.atomic
def enregistrer_agent(request):
    if request.method == 'POST':
        try:
            print("➡️ Requête reçue en POST")

            # 1. Récupération des champs standards
            nom = request.POST.get('nom')
            prenoms = request.POST.get('prenoms')
            email = request.POST.get('email')
            telephone = request.POST.get('telephone')
            nationalite = request.POST.get('nationalite')
            statut = request.POST.get('statut')
            residence = request.POST.get('residence')
            pays_affectation = request.POST.get('pays_affectation')
            libelle_competence = request.POST.get('competences')
            autre_competence = request.POST.get('autre_competence')

            # Création du personnel
            personnel = Personnel.objects.create(
                nom=nom,
                prenoms=prenoms,
                email=email,
                telephone=telephone,
                nationalite=nationalite,
                statut=statut,
                residence=residence
            )

            # 2. Gestion du pays d'affectation → créer si inexistant
            if pays_affectation:
                pays, _ = PaysAffectation.objects.get_or_create(nom_pays=pays_affectation)
                # Date d’expatriation aujourd’hui par défaut (ou à adapter)
                Expatriation.objects.create(
                    personnel=personnel,
                    pays=pays,
                    date_expatriation=parse_date(request.POST.get('date_expatriation')) or timezone.now().date()
                )

            # 3. Gestion de la compétence (avec "AUTRE")
            if libelle_competence:
                if libelle_competence == 'AUTRE':
                    competence, _ = Competence.objects.get_or_create(libelle='AUTRE', autre=autre_competence)
                else:
                    competence, _ = Competence.objects.get_or_create(libelle=libelle_competence)

                Posseder.objects.create(personnel=personnel, competence=competence)

            # 4. Gestion des certificats dynamiques
            certificats = [key.split('[')[1].split(']')[0] for key in request.POST if key.startswith('certificats[')]
            certificats = list(set(certificats))  # Supprimer les doublons

            for cert_id in certificats:
                prefix = f'certificats[{cert_id}]'
                libelle = request.POST.get(f'{prefix}[libelle]')
                type_cert = request.POST.get(f'{prefix}[type]')
                obtention = parse_date(request.POST.get(f'{prefix}[obtention]'))
                validite = parse_date(request.POST.get(f'{prefix}[validite]'))
                statut_cert = request.POST.get(f'{prefix}[statut]')
                organisme = request.POST.get(f'{prefix}[organisme]')
                fichier = request.FILES.get(f'{prefix}[fichier]')
                # Vérification des champs requis
                print(f"Traitement du certificat {cert_id}: {libelle}, {type_cert}, {obtention}, {validite}, {statut_cert}, {organisme}")
            if all([libelle, type_cert, obtention, validite, statut_cert, organisme]):
                Certificat.objects.create(
                    personnel=personnel,
                    libelle=libelle,
                    type=type_cert,
                    date_obtention=obtention,
                    validite=validite,
                    statut=statut_cert,
                    organisme=organisme,
                    fichier_pdf=fichier
                )

            return JsonResponse({'success': True, 'message': 'Agent enregistré avec succès.'})

        except Exception as e:
            print("❌ Erreur :", str(e))
            return JsonResponse({'success': False, 'errors': {'exception': str(e)}}, status=400)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)





# def modifier_agent(request, agent_id):
#     agent = get_object_or_404(Personnel, id=agent_id)
#     competences_ids = list(agent.competences_possedees.values_list('competence_id', flat=True))
#     certificats = agent.certificat_set.all()
#     certificats_data = [{
#         "id": c.id,
#         "libelle": c.libelle,
#         "type": c.type,
#         "date_obtention": c.date_obtention.strftime('%Y-%m-%d') if c.date_obtention else "",
#         "date_validite": c.date_validite.strftime('%Y-%m-%d') if c.date_validite else "",
#         "statut": c.statut,
#         "organisme": c.organisme,
#     } for c in certificats]

#     agent_data = {
#         "id": agent.id,
#         "nom": agent.nom,
#         "prenoms": agent.prenoms,
#         "email": agent.email,
#         "telephone": agent.telephone,
#         "nationalite": agent.nationalite,
#         "statut": agent.statut,
#         "residence": agent.residence,
#         "pays_affectation_actuelle": agent.pays_affectation_actuelle,
#         "competences": competences_ids,
#         "certificats": certificats_data
#     }

#     return JsonResponse(agent_data, safe=False)



def modifier_agent(request, agent_id):
    agent = get_object_or_404(Personnel, pk=agent_id)

    if request.method == 'POST':
        form = ModifierPersonnelForm(request.POST, request.FILES, agent=agent, instance=agent)
        if form.is_valid():
            form.save()
            return redirect('tabpersonels')
    else:
        form = ModifierPersonnelForm(agent=agent, instance=agent)

    return render(request, 'modifier_agent.html', {
        'form': form,
        'agent': agent
    })
    
    
    
    
    
    


@require_POST
@csrf_exempt
def supprimer_agent(request, agent_id):
    try:
        agent = get_object_or_404(Personnel, id=agent_id)
        agent.delete()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)







def creer_equipe(request):
    competence = request.GET.get('competence')  # facultatif : ?competence=RAN par ex.

    if request.method == 'POST':
        equipe_form = EquipeForm(request.POST)
        formset = MembreFormSet(request.POST, queryset=Membre.objects.none())

        if equipe_form.is_valid() and formset.is_valid():
            # Liste des membres valides (personnel + role)
            membres_valides = []
            for form in formset:
                if form.cleaned_data.get('personnel') and form.cleaned_data.get('role'):
                    membres_valides.append((
                        form.cleaned_data['personnel'].id,
                        form.cleaned_data['role']
                    ))

            if len(membres_valides) < 3:
                messages.warning(request, "Une équipe doit contenir au moins 3 membres.")
            elif len(set(m[0] for m in membres_valides)) != len(membres_valides):
                messages.warning(request, "Un même membre ne peut pas apparaître plusieurs fois.")
            else:
                signature_nouvelle = set(membres_valides)

                for equipe in Equipe.objects.all():
                    signature_existante = set(
                        (m.personnel.id, m.role)
                        for m in equipe.membres.all()
                    )
                    if signature_existante == signature_nouvelle:
                        messages.warning(request, f"L'équipe « {equipe.nom} » avec ces membres et rôles existe déjà.")
                        break
                else:
                    equipe = equipe_form.save()
                    for form in formset:
                        cd = form.cleaned_data
                        if cd.get('personnel') and cd.get('role'):
                            membre = form.save(commit=False)
                            membre.equipe = equipe
                            membre.save()
                    messages.success(request, "Équipe créée avec succès.")
                    return redirect('liste_equipes')
    else:
        equipe_form = EquipeForm()
        formset = MembreFormSet(queryset=Membre.objects.none(), form_kwargs={'competence': competence})

    return render(request, 'equipes.html', {
        'equipe_form': equipe_form,
        'formset': formset,
        'competence': competence,
    })



def liste_equipes(request):
    equipes = Equipe.objects.prefetch_related('membres__personnel')

    return render(request, 'liste_equipes.html', {'equipes': equipes})








def logout_view(request):
    return redirect('login')
    
