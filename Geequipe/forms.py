# forms.py
from datetime import timezone
from django import forms
from .models import COMPETENCE_CHOICES, Activite, AffectationProjet, Certificat, Competence, Expatriation, Livrable, Mobilisation, PaysAffectation, Posseder, Projet, Client, Realiser

class ProjetForm(forms.ModelForm):
    client_nom = forms.CharField(label="Nom du client", max_length=100)

    class Meta:
        model = Projet
        fields = ['nom', 'type', 'date_debut', 'date_fin', 'site', 'ville', 'pays', 'statut', 'chef_projet']

        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.client:
            self.fields['client_nom'].initial = self.instance.client.nom

    def save(self, commit=True):
        client_nom = self.cleaned_data.pop('client_nom')
        client, created = Client.objects.get_or_create(nom=client_nom)
        self.instance.client = client
        return super().save(commit=commit)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})






from django.forms import ValidationError, modelformset_factory, BaseModelFormSet
from .models import Equipe, Membre, Personnel

class EquipeForm(forms.ModelForm):
    class Meta:
        model = Equipe
        fields = ['nom']
       


class MembreForm(forms.ModelForm):
    class Meta:
        model = Membre
        fields = ['personnel', 'role']

    def __init__(self, *args, **kwargs):
        competence = kwargs.pop('competence', None)
        super().__init__(*args, **kwargs)
        if competence:
            self.fields['personnel'].queryset = Personnel.objects.filter(
                competences_possedees__competence__libelle=competence
            ).distinct()




class BaseMembreFormSet(BaseModelFormSet):
    def clean(self):
        super().clean() # Appelez d'abord la méthode clean du formset de base

        # Votre validation existante pour le nombre total de formulaires
        total_forms = 0
        for form in self.forms:
            # Compte seulement les formulaires avec des données nettoyées et non marqués pour suppression
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                total_forms += 1
        
        if total_forms < 3 or total_forms > 5:
            raise forms.ValidationError("Vous devez sélectionner entre 3 et 5 membres pour l'équipe.")

        # Maintenant, ajoutez la validation spécifique pour la compétence "Chauffeur" et le rôle
        chauffeur_competence = None
        try:
            chauffeur_competence = Competence.objects.get(libelle="Chauffeur")
        except Competence.DoesNotExist:
            # Si la compétence "Chauffeur" n'existe pas, loguer un avertissement et sauter la validation spécifique
            print("AVERTISSEMENT: La compétence 'Chauffeur' n'a pas été trouvée. La validation de rôle a été ignorée.")
            pass # Ou lever une erreur spécifique si "Chauffeur" est obligatoire pour votre logique

        for form in self.forms:
            # Ignore les formulaires vides ou ceux marqués pour suppression
            if self.can_delete and form.cleaned_data.get('DELETE', False):
                continue 
            if not form.cleaned_data: # Formulaire vide
                continue

            personnel = form.cleaned_data.get('personnel')
            role = form.cleaned_data.get('role')

            if not personnel:
                # Si le personnel n'est pas sélectionné, mais d'autres données sont là, gérer l'erreur
                form.add_error('personnel', "Le membre du personnel doit être sélectionné.")
                continue # Passe au formulaire suivant

            # Vérifie si le personnel sélectionné a la compétence "Chauffeur"
            is_chauffeur = False
            if chauffeur_competence: # Seulement si la compétence "Chauffeur" existe dans la BD
                # Vérifie la relation Posseder
                if Posseder.objects.filter(personnel=personnel, competence=chauffeur_competence).exists():
                    is_chauffeur = True

            if is_chauffeur:
                # Si le personnel EST un chauffeur, le rôle DOIT être "Chauffeur"
                if role != 'Chauffeur':
                    form.add_error('role', "Le rôle doit être 'Chauffeur' pour ce membre du personnel.")
                    # Optionnel: si vous avez rendu le champ readonly, vous pourriez vouloir forcer la valeur ici
                    # form.instance.role = 'Chauffeur'
            else:
                # Si le personnel N'EST PAS un chauffeur, le rôle NE DOIT PAS être "Chauffeur"
                if role == 'Chauffeur':
                    form.add_error('role', "Ce membre du personnel ne possède pas la compétence 'Chauffeur' et ne peut pas avoir ce rôle.")


MembreFormSet = modelformset_factory(
    Membre,
    form=MembreForm,
    formset=BaseMembreFormSet,
    extra=5,
    max_num=5,
    validate_max=True,
    can_delete=False,
)


# class MembreForm(forms.ModelForm):
#     class Meta:
#         model = Membre
#         fields = ['personnel', 'role'] 

#     def __init__(self, *args, **kwargs):
#         # Récupère l'ID du personnel déjà sélectionné (si c'est un formulaire existant)
#         initial_personnel_id = kwargs.get('instance') and kwargs.get('instance').personnel_id

#         super().__init__(*args, **kwargs)

#         # 1. Pré-filtrage du queryset du personnel au chargement initial du formulaire
#         # Par défaut, afficher tous les personnels, mais cette logique sera surtout gérée par JS.
#         self.fields['personnel'].queryset = Personnel.objects.all() 
        
#         # 2. Applique les règles du rôle de chauffeur si un personnel est déjà associé
#         if initial_personnel_id:
#             personnel_instance = Personnel.objects.get(id=initial_personnel_id)
#             self._apply_chauffeur_rules_to_role_field(personnel_instance)
            
#         # Ajoutez des classes CSS pour faciliter le ciblage par JavaScript
#         self.fields['personnel'].widget.attrs['class'] = 'select-personnel-membre'
#         self.fields['role'].widget.attrs['class'] = 'select-role-membre'

#     def _apply_chauffeur_rules_to_role_field(self, personnel_instance):
#         """
#         Rend le champ 'role' en lecture seule et le pré-remplit avec 'Chauffeur'
#         si le personnel a la compétence 'Chauffeur'.
#         """
#         try:
#             chauffeur_competence = Competence.objects.get(libelle="Chauffeur")
            
#             if Posseder.objects.filter(personnel=personnel_instance, competence=chauffeur_competence).exists():
#                 self.fields['role'].initial = 'Chauffeur'
#                 self.fields['role'].widget.attrs['readonly'] = True
#                 self.fields['role'].widget.attrs['disabled'] = True # Désactive pour éviter l'envoi de la valeur (JS devra la gérer)
#                 self.fields['role'].choices = [('Chauffeur', 'Chauffeur')] # N'affiche que "Chauffeur"
#                 self.fields['role'].widget.attrs['title'] = "Ce rôle est défini automatiquement car le membre est un chauffeur."
#             else:
#                 # Si le personnel n'est PAS un chauffeur, assurez-vous que le champ 'role' n'est pas limité
#                 # au cas où il aurait été rendu 'disabled' ou 'readonly' par erreur
#                 self.fields['role'].widget.attrs.pop('readonly', None)
#                 self.fields['role'].widget.attrs.pop('disabled', None)
#                 # Réinitialisez les choix si vous les aviez limités dynamiquement
#                 # self.fields['role'].choices = ROLES_CHOICES # (nécessite d'importer ROLES_CHOICES de votre modèle Membre)
#         except Competence.DoesNotExist:
#             print("AVERTISSEMENT: La compétence 'Chauffeur' n'a pas été trouvée dans la base de données.")
#             pass

# # Votre BaseMembreFormSet (la validation forte côté serveur) reste inchangée
# class BaseMembreFormSet(BaseModelFormSet):
#     def clean(self):
#         super().clean() 

#         total_forms = 0
#         for form in self.forms:
#             if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
#                 total_forms += 1
        
#         if total_forms < 3 or total_forms > 5:
#             raise forms.ValidationError("Vous devez sélectionner entre 3 et 5 membres pour l'équipe.")

#         chauffeur_competence = None
#         try:
#             chauffeur_competence = Competence.objects.get(libelle="Chauffeur")
#         except Competence.DoesNotExist:
#             print("AVERTISSEMENT: La compétence 'Chauffeur' n'a pas été trouvée. La validation de rôle a été ignorée.")
#             pass

#         for form in self.forms:
#             if not form.cleaned_data or (self.can_delete and form.cleaned_data.get('DELETE', False)):
#                 continue 

#             personnel = form.cleaned_data.get('personnel')
#             role = form.cleaned_data.get('role')

#             if not personnel:
#                 form.add_error('personnel', "Le membre du personnel doit être sélectionné.")
#                 continue 

#             is_chauffeur = False
#             if chauffeur_competence:
#                 if Posseder.objects.filter(personnel=personnel, competence=chauffeur_competence).exists():
#                     is_chauffeur = True

#             # -- Logique de validation bidirectionnelle ici --
#             if is_chauffeur:
#                 if role != 'Chauffeur':
#                     form.add_error('role', "Le rôle doit être 'Chauffeur' pour ce membre du personnel.")
#             else: # Personnel n'est pas chauffeur
#                 if role == 'Chauffeur':
#                     form.add_error('role', "Ce membre du personnel ne possède pas la compétence 'Chauffeur' et ne peut pas avoir ce rôle.")

# MembreFormSet = modelformset_factory(
#     Membre,
#     form=MembreForm,
#     formset=BaseMembreFormSet,
#     extra=5,
#     max_num=5,
#     validate_max=True,
#     can_delete=False,
# )


class ModifierPersonnelForm(forms.ModelForm):
    competence = forms.ChoiceField(
        choices=COMPETENCE_CHOICES,
        label="Spécialité",
        required=True
    )

    pays_affectation = forms.CharField(
        max_length=100,
        required=True,
        label="Pays d'affectation"
    )

    certificats = forms.FileField(
    required=False,
    widget=forms.FileInput(),
    label="Certificats (PDF)"
)

    

    class Meta:
        model = Personnel
        fields = [
            'nom', 'prenoms', 'email', 'telephone',
            'nationalite', 'statut', 'residence',
        ]
        widgets = {
            'statut': forms.Select(choices=[
                ('en_cours', 'En cours'),
                ('termine', 'Terminé'),
                ('en_attente', 'En attente'),
                ('suspendu', 'Suspendu')
            ]),
        }

    def __init__(self, *args, **kwargs):
        self.agent = kwargs.pop('agent', None)
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        # Préremplir compétence
        if self.agent:
            try:
                posseder = Posseder.objects.get(personnel=self.agent)
                self.fields['competence'].initial = posseder.competence.libelle
            except Posseder.DoesNotExist:
                pass

            # Préremplir pays affectation
            expatriation = self.agent.expatriations.order_by('-date_expatriation').first()
            if expatriation:
                self.fields['pays_affectation'].initial = expatriation.pays.nom_pays

    def save(self, commit=True):
        agent = super().save(commit=False)

        # Gérer la compétence
        selected_libelle = self.cleaned_data.get('competence')
        competence_obj, _ = Competence.objects.get_or_create(libelle=selected_libelle)

        # Gérer le pays d'affectation
        nom_pays = self.cleaned_data.get('pays_affectation').strip()
        pays_obj, _ = PaysAffectation.objects.get_or_create(nom_pays=nom_pays)

        if commit:
            agent.save()

            # Met à jour ou crée la relation Posseder
            Posseder.objects.update_or_create(
                personnel=agent,
                defaults={'competence': competence_obj}
            )

            # Met à jour ou crée l'Expatriation
            Expatriation.objects.update_or_create(
                personnel=agent,
                defaults={
                    'pays': pays_obj,
                    'date_expatriation': timezone.now().date()
                }
            )

            # Gérer les certificats
            for fichier in self.files.getlist('certificats'):
                Certificat.objects.create(
                    personnel=agent,
                    fichier=fichier
                )

        return agent
    



# class AffectationProjetForm(forms.ModelForm):
#     class Meta:
#         model = AffectationProjet
#         fields = ['projet', 'equipe']
#         widgets = {
#             'projet': forms.Select(attrs={'class': 'form-select'}),
#             'equipe': forms.Select(attrs={'class': 'form-select'}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Filtre le queryset des projets pour n'afficher que les projets 'en_cours'
#         self.fields['projet'].queryset = Projet.objects.filter(statut='en_cours')

#     def clean(self):
#         cleaned_data = super().clean()
#         equipe = cleaned_data.get('equipe')
#         projet = cleaned_data.get('projet')

#         if equipe and projet:
#             # Vérifie si cette équipe spécifique est déjà affectée à ce projet spécifique
#             if AffectationProjet.objects.filter(equipe=equipe, projet=projet).exists():
#                 raise ValidationError("Cette équipe est déjà affectée à ce projet.")
#         return cleaned_data



# class AffectationProjetForm(forms.ModelForm):
#     class Meta:
#         model = AffectationProjet
#         fields = ['projet', 'equipe']
#         widgets = {
#             'projet': forms.Select(attrs={'class': 'form-select', 'id': 'id_projet'}),
#             'equipe': forms.Select(attrs={'class': 'form-select', 'id': 'id_equipe'}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         # Projets en cours
#         projets_en_cours = Projet.objects.filter(statut='en_cours')

#         # Supprimer pour chaque projet les équipes déjà assignées
#         equipe_assignees = AffectationProjet.objects.values_list('equipe_id', flat=True).distinct()
#         self.fields['equipe'].queryset = Equipe.objects.exclude(id__in=equipe_assignees)

#         # Tous les projets en cours
#         self.fields['projet'].queryset = projets_en_cours

class AffectationProjetForm(forms.ModelForm):
    class Meta:
        model = AffectationProjet
        fields = ['projet', 'equipe']
        widgets = {
            'projet': forms.Select(attrs={'class': 'form-select'}),
            'equipe': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['projet'].queryset = Projet.objects.filter(statut='en_cours')

        # Par défaut, aucune restriction sur les équipes
        self.fields['equipe'].queryset = Equipe.objects.all()

        # Si un projet est sélectionné (POST ou initial), on filtre les équipes
        if 'projet' in self.data:
            try:
                projet_id = int(self.data.get('projet'))
                equipe_ids_exclues = AffectationProjet.objects.filter(projet_id=projet_id).values_list('equipe_id', flat=True)
                self.fields['equipe'].queryset = Equipe.objects.exclude(id__in=equipe_ids_exclues)
            except (ValueError, TypeError):
                pass  # Données invalides, pas de filtrage














class ActiviteForm(forms.ModelForm):
    class Meta:
        model = Activite
        fields = ['nom', 'description', 'date_debut', 'date_fin']
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'nom': 'Nom de l\'activité',
            'description': 'Description',
            'date_debut': 'Date de début',
            'date_fin': 'Date de fin',
        }

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')

        if date_debut and date_fin and date_fin < date_debut:
            raise ValidationError("La date de fin ne peut pas précéder la date de début.")
        return cleaned_data

class MobilisationForm(forms.ModelForm):
    class Meta:
        model = Mobilisation
        fields = ['site', 'date_debut', 'date_fin'] # date_debut et date_fin sont redondantes ici si elles sont tirées de l'activité.
                                                  # Si elles sont spécifiques à la mobilisation, gardez-les.
                                                  # Sinon, vous pouvez les retirer et les définir à partir de l'activité dans la vue.
        widgets = {
            'site': forms.TextInput(attrs={'class': 'form-control'}),
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        labels = {
            'site': 'Site de mobilisation',
            'date_debut': 'Date de début de mobilisation',
            'date_fin': 'Date de fin de mobilisation',
        }

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')

        if date_debut and date_fin and date_fin < date_debut:
            raise ValidationError("La date de fin de mobilisation ne peut pas précéder la date de début.")
        return cleaned_data

class RealiserForm(forms.ModelForm):
    class Meta:
        model = Realiser
        fields = ['equipe']
        widgets = {
            'equipe': forms.Select(attrs={'class': 'form-control'}),
            
        }

    def __init__(self, *args, **kwargs):
        equipes_choices = kwargs.pop('equipes_choices', None)
        super().__init__(*args, **kwargs)
        if equipes_choices:
            self.fields['equipe'].queryset = Equipe.objects.filter(id__in=equipes_choices)
            # Ou simplement : self.fields['equipe'].queryset = equipes_choices

class LivrableForm(forms.ModelForm):
    class Meta:
        model = Livrable
        fields = ['nom_livrable']
        widgets = {
            'nom_livrable': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nom_livrable': 'Nom du livrable',
        }
