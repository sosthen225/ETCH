from urllib import request
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from Geequipe.forms import AffectationProjetForm, EquipeForm, MembreFormSet, ModifierPersonnelForm, ProjetForm
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
from .models import COMPETENCE_CHOICES, PAYS_CHOICES, Activite, AffectationProjet, Certificat, Competence, Equipe, Expatriation, Membre, Mobilisation, PaysAffectation, Personnel, Projet, Client, Posseder, Realiser
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
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils.dateparse import parse_date
from django.contrib import messages





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
    ongoing_projects = Projet.objects.filter(statut='en_cours').count()
    projet_encours= Projet.objects.filter(statut='en_cours').order_by('-date_fin')[:10]
    completed_projects_list = Projet.objects.filter(statut='terminé').order_by('-date_fin')[:10] # Obtenir les 5 derniers projets terminés

    # Pour les notifications : Projets se terminant bientôt (par exemple, dans les 30 jours)
    today = date.today()
    one_month_from_now = today + timedelta(days=30)
    upcoming_projects = Projet.objects.filter(
    date_fin__gt=today,
    date_fin__lte=one_month_from_now,
    statut='en_cours'
).order_by('date_fin')

    # # Pour les notifications : Certifications du personnel expirant bientôt (par exemple, dans les 30 jours)
    # expiring_personnel = Personnel.objects.filter(
    #     certification_expiry_date__gt=today,
    #     certification_expiry_date__lte=one_month_from_now
    # ).order_by('certification_expiry_date')


    context = {
        'total_teams': total_teams,
        'ongoing_projects': ongoing_projects,
        'completed_projects': completed_projects,
        'total_personnel': total_personnel,
        'completed_projects_list': completed_projects_list,
        'upcoming_projects': upcoming_projects,
        'projet_encours': projet_encours
       # 'expiring_personnel': expiring_personnel,
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



from django.utils import timezone
def voir_certificats(request, personnel_id):
    agent = get_object_or_404(Personnel, id=personnel_id)
    certificats = agent.certificats.all()
    aujourd_hui = timezone.now().date()
    return render(request, 'certificats_details.html', {'agent': agent, 'certificats': certificats , 'aujourd_hui': aujourd_hui})




def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None
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
            libelle_competence = request.POST.get('competence')
           

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

            libelle_competence = request.POST.get('competence')
            print(f"Valeur de libelle_competence reçue : '{libelle_competence}'") # <<< Ajoutez ceci

            if libelle_competence:
                
                    competence, _ = Competence.objects.get_or_create(libelle=libelle_competence)
                    print(f"Competence trouvée/créée : {competence.libelle}, Créée: {_}")
                    Posseder.objects.create(personnel=personnel, competence=competence)
                    print("Liaison Posseder créée.")
            # 4. Gestion des certificats dynamiques
            certificats = [key.split('[')[1].split(']')[0] for key in request.POST if key.startswith('certificats[')]
            certificats = list(set(certificats))  # Supprimer les doublons

            for cert_id in certificats:
                prefix = f'certificats[{cert_id}]'
                libelle = request.POST.get(f'{prefix}[libelle]')
                type_cert = request.POST.get(f'{prefix}[type]')
                obtention = parse_date(request.POST.get(f'{prefix}[obtention]'))
                validite = parse_date(request.POST.get(f'{prefix}[validite]'))
                organisme = request.POST.get(f'{prefix}[organisme]')
                fichier = request.FILES.get(f'{prefix}[fichier]')
                # Vérification des champs requis
                print(f"Traitement du certificat {cert_id}: {libelle}, {type_cert}, {obtention}, {validite}, {organisme}")
                if all([libelle, type_cert, obtention, validite, organisme]):
                 Certificat.objects.create(
                    personnel=personnel,
                    libelle=libelle,
                    type=type_cert,
                    date_obtention=obtention,
                    validite=validite,
                    organisme=organisme,
                    fichier_pdf=fichier
                )

            return JsonResponse({'success': True, 'message': 'Agent enregistré avec succès.'})

        except Exception as e:
            print("❌ Erreur :", str(e))
            return JsonResponse({'success': False, 'errors': {'exception': str(e)}}, status=400)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)






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
    
    
    
# from django.http import JsonResponse
# from .models import Personnel

# def get_agent_data(request, agent_id):
#     agent = get_object_or_404(Personnel, id=agent_id)

#     data = {
#         'id': agent.id,
#         'nom': agent.nom,
#         'prenoms': agent.prenoms,
#         'email': agent.email,
#         'telephone': agent.telephone,
#         'nationalite': agent.nationalite,
#         'statut': agent.statut,
#         'residence': agent.residence,
#         'pays_affectation_actuelle': agent.pays_affectation_actuelle,
#         'competences': list(agent.competences.values_list('id', flat=True)),
#         'certificats': [
#             {
#                 'id': cert.id,
#                 'libelle': cert.libelle,
#                 'type': cert.type,
#                 'date_obtention': cert.date_obtention.strftime('%Y-%m-%d') if cert.date_obtention else '',
#                 'date_validite': cert.date_validite.strftime('%Y-%m-%d') if cert.date_validite else '',
#                 'organisme': cert.organisme,
#                 'fichier_url': cert.fichier.url if cert.fichier else ''
#             } for cert in agent.certificats.all()
#         ]
#     }

#     return JsonResponse(data)  
    
# def modifier_agent(request, agent_id):
#     agent = get_object_or_404(Personnel, id=agent_id)

#     if request.method == 'POST':
#         form = ModifierPersonnelForm(request.POST, request.FILES, instance=agent)
#         if form.is_valid():
#             form.save()
#             return JsonResponse({'success': True})
#         else:
#             return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    
#     return JsonResponse({'error': 'Invalid request'}, status=400)


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


from django.views.decorators.http import require_GET

@require_GET
def equipes_disponibles(request):
    projet_id = request.GET.get('projet_id')
    if projet_id:
        equipe_ids = AffectationProjet.objects.filter(projet_id=projet_id).values_list('equipe_id', flat=True)
        equipes = Equipe.objects.exclude(id__in=equipe_ids).values('id', 'nom')
        return JsonResponse(list(equipes), safe=False)
    return JsonResponse([], safe=False)

@require_GET
def projets_disponibles(request):
    equipe_id = request.GET.get('equipe_id')
    if equipe_id:
        projet_ids = AffectationProjet.objects.filter(equipe_id=equipe_id).values_list('projet_id', flat=True)
        projets = Projet.objects.filter(statut='en_cours').exclude(id__in=projet_ids).values('id', 'nom')
        return JsonResponse(list(projets), safe=False)
    return JsonResponse([], safe=False)






def affecter_equipe(request):
    
    if request.method == 'POST':
        form = AffectationProjetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Équipe affectée au projet avec succès.")
            return redirect('affecter_equipe')  # Redirige pour éviter la double soumission
        else:
            # Si le formulaire n'est pas valide, messages.error peut afficher les erreurs de validation
            # Le formulaire contiendra automatiquement les erreurs non liées aux champs (comme celle de clean())
            # et les erreurs spécifiques aux champs.
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = AffectationProjetForm()

    affectations = AffectationProjet.objects.select_related('projet', 'equipe').order_by('-date_affectation')

    return render(request, 'affectation_projet.html', {
        'form': form,
        'affectations': affectations

    })



def supprimer_affectation(request, affectation_id):
    affectation = get_object_or_404(AffectationProjet, id=affectation_id)

    # Vérifie si le projet est encore en cours
    if affectation.projet.statut != 'en_cours':
        messages.error(request, "Impossible de supprimer une affectation pour un projet terminé.")
        return redirect('affecter_equipe')

    if request.method == 'POST':
        affectation.delete()
        messages.success(request, "Affectation supprimée avec succès.")
        return redirect('affecter_equipe')





# def liste_affectations(request):
#     affectations = AffectationProjet.objects.select_related('projet', 'equipe')
#     return render(request, 'liste_affectations.html', {'affectations': affectations})



def mobiliser_equipes(request, projet_id):
    projet = get_object_or_404(Projet, id=projet_id)
    equipes = projet.affectationprojet_set.all()
    return render(request, 'mobilisation.html', {
        'projet': projet,
        'equipes': equipes,
    })



def creer_mobilisation(request, projet_id):
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Exemple de récupération des équipes déjà affectées à ce projet
    equipes_affectees = Equipe.objects.filter(
        activites_realisees__activite__projet=projet
    ).distinct()

    if request.method == 'POST':
        nom_activite = request.POST.get('nom_activite')
        description = request.POST.get('description')
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')
        site = request.POST.get('site')
        equipe_ids = request.POST.getlist('equipes')
        statut = request.POST.get('statut', 'Planifiée')  # exemple
        chef_projet = request.user.chefprojet  # lien avec User supposé

        # Création de l'activité
        activite = Activite.objects.create(
            projet=projet,
            nom=nom_activite,
            description=description,
            statut=statut,
            date_debut=date_debut,
            date_fin=date_fin,
            temps_passe=timedelta(),  # vide au départ
        )

        # Création de la mobilisation
        mobilisation = Mobilisation.objects.create(
            activite=activite,
            chef_projet=chef_projet,
            date_debut=date_debut,
            date_fin=date_fin,
            site=site
        )

        # Assigner les équipes
        for equipe_id in equipe_ids:
            Realiser.objects.create(
                equipe_id=equipe_id,
                activite=activite,
                date=date_debut
            )

        return redirect('mobilisation.html')

    return render(request, 'organiser_mobilisation.html' ,{
        'projet': projet,
        'equipes': equipes_affectees,
        
    })



# from django.db.models import Prefetch

# def organiser_mobilisation(request):
#     # Charger les projets "en cours" + leurs affectations avec les équipes associées
#     affectations = Projet.objects.filter(statut='en_cours').prefetch_related(
#     Prefetch(
#             'equipe_affectee', 
#             queryset=AffectationProjet.objects.select_related('equipe')
#         )
#     )

#     return render(request, 'mobilisation.html', {'affectations': affectations})


def organiser_mobilisation(request):
    
    # Récupérer les projets "en cours" ayant au moins une affectation liée
    projets = Projet.objects.filter(
        statut='en_cours',
        equipe_affectee__isnull=False  # relation inversée de AffectationProjet
    ).distinct()  # éviter les doublons si plusieurs équipes
    print("Projet:", projets)

    #  Préparation des données pour le template
    data = []
    for projet in projets:
        # On récupère les affectations pour ce projet
        affectations = AffectationProjet.objects.filter(projet=projet).select_related('equipe')

        # On extrait les équipes à partir des affectations
        equipes = [a.equipe for a in affectations]
        print("Projet:", projet.nom, "Équipes:", [e.nom for e in equipes])
        # On construit une entrée dans la liste finale
        data.append({
            'projet': projet,
            'equipes': equipes
        })

   

    return render(request, 'mobilisation.html', {'projets_data': data})




from django.db.models import Q
def search_results(request):
    query = request.GET.get('q') # Récupère le terme de recherche
    
    # Initialise un dictionnaire pour stocker les résultats de chaque catégorie
    results = {
        'projets': [],
        'personnel': [],
        'equipes': [],
    }

    if query:
        # --- Recherche dans le modèle Projet ---
        projets_filters = Q() # Crée un objet Q vide pour construire les conditions

        # Champs textuels : Utilisez __icontains
        projets_filters |= Q(nom__icontains=query) 

        # Si 'client' est un CharField (un simple champ texte dans le modèle Projet)
        # projets_filters |= Q(client__icontains=query) 
        
        # SI 'client' est une ForeignKey vers un modèle 'Client' qui a un champ 'nom' (ou 'entreprise', 'raison_sociale'...)
        # Alors, traversez la relation :
        projets_filters |= Q(client__nom__icontains=query) 
        # projets_filters |= Q(client__entreprise__icontains=query) # Exemple si le champ est 'entreprise'

        # Champ de date (date_fin) : 
        # Vous devez gérer les dates différemment.
        # Par exemple, si l'utilisateur entre une année :
        try:
            year = int(query)
            projets_filters |= Q(date_fin__year=year) # Recherche par année exacte
        except ValueError:
            # Si 'query' n'est pas un nombre, ignore la recherche par année.
            pass
        # Ou si vous voulez permettre une recherche par mois/jour, c'est plus complexe et dépend
        # du format de la requête de l'utilisateur.

        projets_results = Projet.objects.filter(projets_filters).distinct()


        # --- Recherche dans le modèle Personnel ---
        personnel_filters = Q()

        # Champs textuels et email : Utilisez __icontains
        personnel_filters |= Q(nom__icontains=query) 
        personnel_filters |= Q(prenoms__icontains=query)
        personnel_filters |= Q(email__icontains=query)

        # Champ téléphone (chiffres, souvent stocké en CharField pour garder les + et les espaces)
        # Si 'telephone' est un CharField :
        personnel_filters |= Q(telephone__icontains=query)
        # Si 'telephone' est un IntegerField, vous devrez le convertir en chaîne pour la recherche,
        # mais c'est moins commun et moins performant que de le stocker en CharField.

        # Champ 'statut' :
        # Si 'statut' est un CharField (ex: 'Actif', 'En congé')
        personnel_filters |= Q(statut__icontains=query) 
        
        # SI 'statut' est une ForeignKey vers un modèle 'Statut' (ex: avec un champ 'libelle' ou 'nom')
        # ALORS traversez la relation :
        # personnel_filters |= Q(statut__libelle__icontains=query) 
        # personnel_filters |= Q(statut__nom__icontains=query)

        personnel_results = Personnel.objects.filter(personnel_filters).distinct()


        # --- Recherche dans le modèle Equipe ---
        equipes_filters = Q()

        # Champ textuel : Utilisez __icontains
        equipes_filters |= Q(nom__icontains=query)

        # Champ de date (date_creation) : NE PAS utiliser __icontains.
        # Même logique que pour 'date_fin' dans Projet.
        try:
            year = int(query)
            equipes_filters |= Q(date_creation__year=year) # Recherche par année exacte
        except ValueError:
            pass

        equipes_results = Equipe.objects.filter(equipes_filters).distinct()


        # Assignation des résultats
        results['projets'] = projets_results
        results['personnel'] = personnel_results
        results['equipes'] = equipes_results

    # Rend le template search_results.html avec la requête et les résultats
    return render(request, 'recherche_sur_lesite.html', {'query': query, 'results': results})




def logout_view(request):
    return redirect('login')
    
