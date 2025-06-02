from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# ----------- CONSTANTES POUR LES CHOIX -----------

PAYS_CHOICES = [
    ('CI', 'Côte d’Ivoire'),
    ('BF', 'Burkina Faso'),
    ('ML', 'Mali'),
    ('SN', 'Sénégal'),
    ('GN', 'Guinée'),
]

COMPETENCE_CHOICES = [
    ('RAN', 'RAN'),
    ('CORE', 'CORE'),
    ('DRIVE_TEST', 'DRIVE TEST'),
    ('AUTRE', 'AUTRE'),
]

ROLE_CHOICES = [
    ('monteur', 'Monteur'),
    ('chauffeur', 'Chauffeur'),
    ('technicien', 'Technicien'),
]

# ----------- MODELES -----------

class PaysAffectation(models.Model):
    nom_pays = models.CharField(max_length=100, choices=PAYS_CHOICES)

    def __str__(self):
        return self.nom_pays


class Personnel(models.Model):
    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    nationalite = models.CharField(max_length=50)
    statut = models.CharField(max_length=50)
    residence = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.prenoms} {self.nom}"


class ChefProjet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='chef_projet')

    def __str__(self):
        return self.user.username

   


class Client(models.Model):
    nom = models.CharField(max_length=100)

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
    chef_projet = models.ForeignKey(ChefProjet, on_delete=models.CASCADE, related_name='projets')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projets')

    def __str__(self):
        return self.nom


class Equipe(models.Model):
    nom = models.CharField(max_length=100)
    date_creation = models.DateField()
    date_dissolution = models.DateField(null=True, blank=True)

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
    autre = models.CharField(max_length=100, blank=True, null=True)

    def clean(self):
        if self.libelle == 'AUTRE' and not self.autre:
            raise ValidationError("Le champ 'autre' est requis si la compétence est 'AUTRE'.")

    def __str__(self):
        return self.autre if self.libelle == 'AUTRE' else self.libelle


class Posseder(models.Model):
    personnel = models.ForeignKey('Personnel', on_delete=models.CASCADE, related_name='competences_possedees')
    competence = models.ForeignKey('Competence', on_delete=models.CASCADE, related_name='personnels')

    def __str__(self):
        return f"{self.personnel} possède {self.competence}"


class Activite(models.Model):
    projet = models.ForeignKey('Projet', on_delete=models.CASCADE, related_name='activites')
    nom = models.CharField(max_length=100)
    description = models.TextField()
    statut = models.CharField(max_length=50)
    date_debut = models.DateField()
    date_fin = models.DateField()
    temps_passe = models.DurationField()

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

    def __str__(self):
        return self.libelle


class Realiser(models.Model):
    equipe = models.ForeignKey('Equipe', on_delete=models.CASCADE, related_name='activites_realisees')
    activite = models.ForeignKey('Activite', on_delete=models.CASCADE, related_name='equipes_realisation')
    date = models.DateField()

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

    def __str__(self):
        return f"Mobilisation de {self.chef_projet} pour {self.activite}"


class AffectationProjet(models.Model):
    equipe = models.ForeignKey('Equipe', on_delete=models.CASCADE, related_name='affectations_projet')

    def __str__(self):
        return f"Affectation de {self.equipe}"


class Noter(models.Model):
    chef_projet = models.ForeignKey('ChefProjet', on_delete=models.CASCADE, related_name='notations')
    personnel = models.ForeignKey('Personnel', on_delete=models.CASCADE, related_name='notes')
    ponctualite = models.IntegerField()
    respect = models.IntegerField()
    performance = models.IntegerField()

    def __str__(self):
        return f"Note de {self.personnel}"


class Evaluer(models.Model):
    chef_projet = models.ForeignKey('ChefProjet', on_delete=models.CASCADE, related_name='evaluations')
    equipe = models.ForeignKey('Equipe', on_delete=models.CASCADE, related_name='evaluations')
    ponctualite = models.IntegerField()
    respect = models.IntegerField()
    performance = models.IntegerField()

    def __str__(self):
        return f"Évaluation de {self.equipe}"


class Expatriation(models.Model):
    personnel = models.ForeignKey('Personnel', on_delete=models.CASCADE, related_name='expatriations')
    pays = models.ForeignKey('PaysAffectation', on_delete=models.CASCADE, related_name='expatriations')
    date_expatriation = models.DateField()

    def __str__(self):
        return f"{self.personnel} expatrié en {self.pays}"
