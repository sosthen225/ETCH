from datetime import timedelta, date
import random
from faker import Faker
from django.utils import timezone

# Import des modèles
from Geequipe.models import (
    PaysAffectation, Personnel, ChefProjet, Client, Equipe,
    Projet, Membre, Competence, Posseder, Activite, Livrable,
    Certificat, Expatriation, AffectationProjet,
    Effectuer, Realiser
)
from django.contrib.auth.models import User

fake = Faker('fr_FR')

# --- Liste de villes ivoiriennes ---
VILLE_IVOIRIENNE = [
    "Abidjan", "Bouaké", "Daloa", "Gagnoa", "San-Pédro",
    "Korhogo", "Man", "Bondoukou", "Sassandra", "Agboville",
    "Tiassalé", "Yamoussoukro", "Divo", "Aboisso", "Toumodi"
]

def fake_ville():
    return random.choice(VILLE_IVOIRIENNE)

# --- 1. Créer tous les pays d'expatriation ---
def create_pays():
    PAYS_CHOICES = [
        ("COTE D'IVOIRE", "COTE D'IVOIRE")
        
    ]
    for nom in PAYS_CHOICES:
        PaysAffectation.objects.get_or_create(nom_pays=nom[0])

# --- 2. Créer maximum 2 chefs de projet ---
def create_chef_projets():
    chefs = []

    # Chef 1 : DFalikou - Diomandé Falikou
    user_df, created_df = User.objects.get_or_create(
        username='DFalikou',
        defaults={'email': 'diomande@gmail.com'}
    )
    if created_df:
        user_df.set_password('etech2025')  # Mot de passe
        user_df.save()

    chef_df, _ = ChefProjet.objects.get_or_create(user=user_df)
    chefs.append(chef_df)

    # Chef 2 : Dominique - N'Guessan Dominique
    user_dn, created_dn = User.objects.get_or_create(
        username='Dominique',
        defaults={'email': 'dominique@gmail.com'}
    )
    if created_dn:
        user_dn.set_password('etech2025')  # Mot de passe
        user_dn.save()

    chef_dn, _ = ChefProjet.objects.get_or_create(user=user_dn)
    chefs.append(chef_dn)

    return chefs

# --- 3. Créer des clients ---
def create_clients(n=50):
    for _ in range(n):
        Client.objects.get_or_create(nom=fake.company())

# --- 4. Récupérer ou créer les compétences fixes ---
def get_competences():
    COMPETENCE_CHOICES = ['RAN', 'CORE', 'DRIVE_TEST', 'OPTIMISATION', 'CHAUFFEUR']
    competences = []
    for libelle in COMPETENCE_CHOICES:
        comp, _ = Competence.objects.get_or_create(libelle=libelle)
        competences.append(comp)
    return competences

# --- 5. Créer des personnels avec exactement 1 compétence ---
def create_personnels(n=50):
    nationalites = ['Ivoirienne', 'Burkinabée', 'Béninoise', 'Togolaise', 'Congolaise', 'Sénégalaise']
    competences = get_competences()

    for _ in range(n):
        p = Personnel.objects.create(
            nom=fake.last_name(),
            prenoms=fake.first_name(),
            email=fake.email(),
            telephone=fake.random_number(digits=10),
            nationalite=random.choice(nationalites),
            residence=fake_ville()
        )

        competence = random.choice(competences)
        Posseder.objects.create(personnel=p, competence=competence)

        if competence.libelle == 'CHAUFFEUR':
            p.statut = 'ACTIF'
            p.save()

        date_obtention = fake.date_between(start_date='-3y', end_date='+2y')
        validite = date_obtention + timedelta(days=730)  # Valide 2 ans
        Certificat.objects.create(
            personnel=p,
            libelle="Certificat de compétence",
            type="Technique",
            date_obtention=date_obtention,
            validite=validite,
            organisme="Organisme fictif"
        )

        pays = PaysAffectation.objects.order_by('?').first()
        if pays:
            Expatriation.objects.create(
                personnel=p,
                pays=pays,
                date_expatriation=fake.date_between(start_date='-1y', end_date='today')
            )

# --- 6. Créer des équipes ---
def create_equipes(n=20):
    personnels = list(Personnel.objects.all())
    roles = ['monteur', 'technicien', 'chauffeur', "chef d'équipe"]

    # Récupérer les compétences
    competence_chauffeur = Competence.objects.get(libelle='CHAUFFEUR')
    competence_monteur = Competence.objects.get(libelle='RAN')  # exemple
    competence_technicien = Competence.objects.get(libelle='CORE')  # exemple

    for i in range(n):
        # Choisir un chef d'équipe aléatoirement
        chef = random.choice(personnels)

        # Définir si l’équipe aura 3 ou 5 membres
        equipe_size = random.choice([3, 5])

        # Générer un nom unique basé sur le chef + itération
        numero_unique = f"{i+1:03d}"
        nom_equipe = f"Équipe_{chef.id}_Team_#{numero_unique}"

        equipe = Equipe.objects.create(nom=nom_equipe)

        # --- Chef d'équipe ---
        Membre.objects.create(
            personnel=chef,
            equipe=equipe,
            role="chef d'équipe"
        )

        # --- Sélectionner des autres personnels ---
        autres_personnels = [p for p in personnels if p.id != chef.id]

        # Liste des rôles à attribuer selon la taille de l’équipe
        if equipe_size == 3:
            roles_a_attribuer = ["technicien", "chauffeur"]
        else:  # equipe_size == 5
            roles_a_attribuer = ["technicien", "monteur", "monteur", "chauffeur"]

        membres_selectionnes = []

        for role in roles_a_attribuer:
            while True:
                p = random.choice(autres_personnels)

                # Si c’est un chauffeur, vérifier qu’il a la compétence CHAUFFEUR
                posseder = p.competences_possedees.first()
                if posseder and posseder.competence.libelle == 'CHAUFFEUR' and role == "chauffeur":
                    if p not in membres_selectionnes:
                        membres_selectionnes.append(p)
                        break
                elif posseder and role != "chauffeur":
                    if p not in membres_selectionnes:
                        membres_selectionnes.append(p)
                        break

            Membre.objects.create(
                personnel=p,
                equipe=equipe,
                role=role
            )

# --- 7. Créer des projets et activités liées aux réseaux télécoms ---
def create_projets(n=50):
    chefs = create_chef_projets()
    clients = list(Client.objects.all())
    equipes = list(Equipe.objects.all())

    themes_projets = [
        "Déploiement Réseau Mobile", "Optimisation Réseau 4G", "Installation Fibre Optique",
        "Mise en place BTS", "Maintenance Infrastructure Télécom", "Extension Réseau Urbain"
    ]

    tous_les_pays = [p.nom_pays for p in PaysAffectation.objects.all()]

    for i in range(n):
        debut = fake.date_between(start_date=date(2024, 10, 1), end_date=date(2025, 9, 30))
        fin = debut + timedelta(days=random.randint(30, 365))
        client = random.choice(clients)
        chef = random.choice(chefs)

        pays_projet = random.choice(tous_les_pays)

        # Générer une ville selon le pays
        if pays_projet == "COTE D'IVOIRE":
            ville_projet = fake_ville()  # ← Pas d’argument ici
        else:
            ville_projet = fake.city()

        projet = Projet.objects.create(
            nom=f"{random.choice(themes_projets)} {i+1}",
            type=random.choice(['Infra', 'Réseau', 'Maintenance']),
            date_debut=debut,
            date_fin=fin,
            site=f"{ville_projet} - {fake.street_address()}",
            ville=ville_projet,
            pays=pays_projet,
            chef_projet=chef,
            client=client
        )

        equipe = random.choice(equipes)
        AffectationProjet.objects.create(equipe=equipe, projet=projet)
        create_activites(projet)



# --- 8. Créer des activités avec livrables obligatoires ---
def create_activites(projet):
    themes_activites = [
        "Installation équipements", "Configuration routeurs", "Test signalisation",
        "Déploiement fibre optique", "Optimisation bande passante", "Maintenance câblage",
        "Contrôle qualité", "Formation terrain", "Audit infrastructure"
    ]
    descriptions = {
        "Installation équipements": "Pose des équipements radio sur site.",
        "Configuration routeurs": "Configuration des équipements réseau principaux.",
        "Test signalisation": "Tests fonctionnels des protocoles de transmission.",
        "Déploiement fibre optique": "Installation de tronçons de fibre optique.",
        "Optimisation bande passante": "Réglages pour améliorer la qualité du trafic.",
        "Maintenance câblage": "Diagnostic et remplacement des câbles défectueux.",
        "Contrôle qualité": "Vérification des normes techniques sur site.",
        "Formation terrain": "Apprentissage des procédures aux techniciens locaux.",
        "Audit infrastructure": "Inspection complète des infrastructures existantes."
    }

    for _ in range(random.randint(2, 5)):  # 2 à 5 activités par projet
        debut_act = fake.date_between(start_date=projet.date_debut, end_date=projet.date_fin)
        fin_act = debut_act + timedelta(days=random.randint(1, 15))

        activite = Activite.objects.create(
            projet=projet,
            nom=random.choice(themes_activites),
            description=descriptions[random.choice(list(descriptions.keys()))],
            statut=random.choice(['en cours', 'planifiée']),
            date_debut=debut_act,
            date_fin=fin_act
        )

        types_livrables = ["Rapport technique", "Plan topo", "Photo installation", "Guide utilisateur"]
        Livrable.objects.create(
            activite=activite,
            nom_livrable=f"{random.choice(types_livrables)} - {activite.nom}"
        )

        equipe = projet.equipes.first()
        if equipe:
            create_effectuers(activite, equipe)
            create_realiser(activite, equipe)

# --- 9. Créer des effectuers (membre → activité) ---
def create_effectuers(activite, equipe):
    membres = Membre.objects.filter(equipe=equipe)
    for membre in membres:
        Effectuer.objects.create(membre=membre, activite=activite)

# --- 10. Créer des réalisations (équipe → activité) ---
def create_realiser(activite, equipe):
    Realiser.objects.create(equipe=equipe, activite=activite)

# --- 11. Fonction principale ---
def run():
    print("1/ Génération des pays...")
    create_pays()

    print("2/ Génération des compétences...")
    get_competences()

    print("3/ Génération des chefs de projet...")
    create_chef_projets()

    print("4/ Génération des clients...")
    create_clients()

    print("5/ Génération des personnels...")
    create_personnels()

    print("6/ Génération des équipes...")
    create_equipes()

    print("7/ Génération des projets et activités...")
    create_projets()

    print("✅ Données générées avec succès !")
