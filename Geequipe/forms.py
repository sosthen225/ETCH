# forms.py
from datetime import timezone
from django import forms
from .models import COMPETENCE_CHOICES, AffectationProjet, Certificat, Competence, Expatriation, PaysAffectation, Posseder, Projet, Client

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
        super().clean()
        total_forms = len([form for form in self.forms if form.cleaned_data and not form.cleaned_data.get('DELETE', False)])
        if total_forms < 3 or total_forms > 5:
            raise forms.ValidationError("Vous devez sélectionner entre 3 et 5 membres pour l'équipe.")

MembreFormSet = modelformset_factory(
    Membre,
    form=MembreForm,
    formset=BaseMembreFormSet,
    extra=5,
    max_num=5,
    validate_max=True,
    can_delete=False,
    
)



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