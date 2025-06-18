from datetime import timezone
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


# ----------- CONSTANTES POUR LES CHOIX -----------

PAYS_CHOICES = [
    ("COTE D'IVOIRE", "COTE D'IVOIRE"),
    ('BURKINA FASO', 'BURKINA FASO'),
    ('BENIN', 'BENIN'),
    ('TOGO', 'TOGO'),
    ('NIGER','NIGER'),

    ('SENEGAL', 'SENEGAL'),
    ('GABON', 'GABON'),
    ('CAMEROUN','CAMEROUN'),
    ('CONGO', 'CONGO'),
     ('GUINEE', 'GUINEE'),
    ('MALI', 'MALI'),
    ('CENTRAFRIQUE', 'CENTRAFRIQUE'),
    ('TCHAD', 'TCHAD'),
    ('REPUBLIQUE DEMOCRATIQUE DU CONGO', 'REPUBLIQUE DEMOCRATIQUE DU CONGO',),
    
]

COMPETENCE_CHOICES = [
    ('RAN', 'RAN'),
    ('CORE', 'CORE'),
    ('DRIVE_TEST', 'DRIVE TEST'),
    ('OPTIMISATION', 'OPTIMISATION'),
   ('CHAUFFEUR', 'CHAUFFEUR')
    
]

ROLE_CHOICES = [
    ('monteur', 'Monteur'),
    ('chauffeur', 'Chauffeur'),
    ('technicien', 'Technicien'),
    ("chef d'equipe", "Chef d'equipe")
]

STATUT_PERSONNEL_CHOICES = [
    ('DISPONIBLE', 'Disponible'),
    ('ACTIF', 'Actif'),
    ('CONGE', 'En congé'),
    ('SUSPENDU', 'Suspendu'),
    ('MISSION', 'En mission')
]


STATUT_ACTIVITIES_CHOICES = [
    ('en cours', 'En cours'),
    ('terminée', 'Terminée'),
    ('planifiée' , 'planifiée'),
    ('suspendue','Suspendue') ]


# ----------- MODELES -----------

class PaysAffectation(models.Model):
    nom_pays = models.CharField(max_length=100, choices=PAYS_CHOICES)

    def __str__(self):
        return self.nom_pays


class Personnel(models.Model):
    
    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=10,unique=True)
    nationalite = models.CharField(max_length=50)
    statut = models.CharField (max_length=50, choices= STATUT_PERSONNEL_CHOICES ,default='actif')
    residence = models.CharField(max_length=100)
    competences = models.ManyToManyField('Competence', through='Posseder', related_name='personnel')

    @property
    def statut_choices(self):
        return self.STATUT_CHOICES
    
    def __str__(self):
        return f"{self.prenoms} {self.nom}"
    def get_pays_affectation_actuelle(self):
        """
        Retourne le dernier pays d'expatriation (le plus récent).
        """
        derniere_expat = self.expatriations.order_by('-date_expatriation').first()
        return derniere_expat.pays.nom_pays if derniere_expat else "Aucune affectation"
    
    

class ChefProjet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='chef_projet')
    def __str__(self):
        return self.user.username

   


class Client(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom


class Equipe(models.Model):
    nom = models.CharField(max_length=100,unique=True)
    date_creation = models.DateField(auto_now_add=True)
   

    def __str__(self):
        return self.nom

class Projet(models.Model):
    nom = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    date_debut = models.DateField()
    date_fin = models.DateField()
    site = models.CharField(max_length=100)
    ville = models.CharField(max_length=100)
    pays = models.CharField(max_length=100)
    statut = models.CharField(max_length=50, choices=[('en cours', 'En cours'), ('terminé', 'Terminé'), ('en attente' , 'En attente'),('suspendu','Suspendu') ], default='en cours')
    chef_projet = models.ForeignKey(ChefProjet, on_delete=models.CASCADE, related_name='projets')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projets')
    equipes = models.ManyToManyField(Equipe, through='AffectationProjet', related_name='projets')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
      if self.date_fin < self.date_debut:
        raise ValidationError("La date de fin ne peut pas être antérieure à la date de début.")


    def __str__(self):
        return self.nom





class Membre(models.Model):
    personnel = models.ForeignKey('Personnel', on_delete=models.CASCADE, related_name='membres')
    equipe = models.ForeignKey('Equipe', on_delete=models.CASCADE, related_name='membres')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.personnel} - {self.get_role_display()}"


class Competence(models.Model):
    libelle = models.CharField(max_length=50, choices=COMPETENCE_CHOICES)
    

    def __str__(self):
        return self.libelle


class Posseder(models.Model):
    personnel = models.ForeignKey('Personnel', on_delete=models.CASCADE, related_name='competences_possedees')
    competence = models.ForeignKey('Competence', on_delete=models.CASCADE, related_name='personnels')

    def __str__(self):
        return f"{self.personnel} possède {self.competence}"


class Activite(models.Model):
    projet = models.ForeignKey('Projet', on_delete=models.CASCADE, related_name='activites')
    nom = models.CharField(max_length=100)
    description = models.TextField()
    statut = models.CharField(max_length=20,choices=STATUT_ACTIVITIES_CHOICES, default='planifiée')
    date_debut = models.DateField()
    date_fin = models.DateField()
    temps_passe = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
     if self.date_fin < self.date_debut:
        raise ValidationError("La date de fin ne peut pas être antérieure à la date de début.")


    def __str__(self):
        return self.nom


class Effectuer(models.Model):
    personnel = models.ForeignKey('Personnel', on_delete=models.CASCADE, related_name='activites_effectuees')
    activite = models.ForeignKey('Activite', on_delete=models.CASCADE, related_name='personnels_affectes')
    date_affecter = models.DateField()

    def __str__(self):
        return f"{self.personnel} affecté à {self.activite}"


class Certificat(models.Model):
    personnel = models.ForeignKey('Personnel', on_delete=models.CASCADE, related_name='certificats')
    libelle = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    date_obtention = models.DateField()
    validite = models.DateField()
    organisme = models.CharField(max_length=100)
    fichier_pdf = models.FileField(upload_to='certificats/', null=True, blank=True)


    @property
    def statut(self):
        aujourdhui = timezone.now().date()
        if self.validite < aujourdhui:
            return 'expire'
        elif self.validite == aujourdhui:
            return 'expire_aujourdhui' 
        elif (self.validite - aujourdhui).days <= 30:  # Validité dans les 30 jours
            return 'bientot_expire'
        else:
            return 'a_jour'

    def __str__(self):
        return self.libelle


class Realiser(models.Model):
    equipe = models.ForeignKey('Equipe', on_delete=models.CASCADE, related_name='activites_realisees')
    activite = models.ForeignKey('Activite', on_delete=models.CASCADE, related_name='equipes_realisation')
    date = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.equipe} a réalisé {self.activite}"


class Livrable(models.Model):
    activite = models.ForeignKey('Activite', on_delete=models.CASCADE, related_name='livrables')
    nom_livrable = models.CharField(max_length=100)

    def __str__(self):
        return self.nom_livrable


class Mobilisation(models.Model):
    activite = models.ForeignKey('Activite', on_delete=models.CASCADE, related_name='mobilisations')
    chef_projet = models.ForeignKey('ChefProjet', on_delete=models.CASCADE, related_name='mobilisations')
    date_debut = models.DateField()
    date_fin = models.DateField()
    site = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def clean(self):
     if self.date_fin < self.date_debut:
        raise ValidationError("La date de fin ne peut pas être antérieure à la date de début.")


    def __str__(self):
        return f"Mobilisation de {self.chef_projet} pour {self.activite}"


class AffectationProjet(models.Model):
    equipe = models.ForeignKey('Equipe', on_delete=models.CASCADE, related_name='affectations_projet')
    projet = models.ForeignKey('Projet', on_delete=models.CASCADE, related_name='equipe_affectee')
    date_affectation=models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('equipe', 'projet')
        verbose_name = "Affectation à un projet"
        verbose_name_plural = "Affectations à des projets"

    def __str__(self):
        return f"{self.equipe} affectée au projet {self.projet}"



class Noter(models.Model):
    chef_projet = models.ForeignKey('ChefProjet', on_delete=models.CASCADE, related_name='notations')
    personnel = models.ForeignKey('Personnel', on_delete=models.CASCADE, related_name='notes')
    ponctualite = models.IntegerField()
    respect = models.IntegerField()
    performance = models.IntegerField()

    def clean(self):
     for field in ['ponctualite', 'respect', 'performance']:
        note = getattr(self, field)
        if not (0 <= note <= 20):
            raise ValidationError(f"La note de {field} doit être entre 0 et 20.")


    def __str__(self):
        return f"Note de {self.personnel}"


class Evaluer(models.Model):
    chef_projet = models.ForeignKey('ChefProjet', on_delete=models.CASCADE, related_name='evaluations')
    equipe = models.ForeignKey('Equipe', on_delete=models.CASCADE, related_name='evaluations')
    ponctualite = models.IntegerField()
    respect = models.IntegerField()
    performance = models.IntegerField()

    
    def clean(self):
      for field in ['ponctualite', 'respect', 'performance']:
        note = getattr(self, field)
        if not (0 <= note <= 20):
            raise ValidationError(f"La note de {field} doit être entre 0 et 20.")


    def __str__(self):
        return f"Évaluation de {self.equipe}"


class Expatriation(models.Model):
    personnel = models.ForeignKey('Personnel', on_delete=models.CASCADE, related_name='expatriations')
    pays = models.ForeignKey('PaysAffectation', on_delete=models.CASCADE, related_name='expatriations')
    date_expatriation = models.DateField()

    def __str__(self):
        return f"{self.personnel} expatrié en {self.pays.nom_pays} ({self.date_expatriation})"