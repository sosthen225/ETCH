# forms.py
from django import forms
from .models import Projet, Client

class ProjetForm(forms.ModelForm):
    client_nom = forms.CharField(label="Nom du client", max_length=100)

    class Meta:
        model = Projet
        fields = ['nom', 'type', 'date_debut', 'date_fin', 'site', 'ville', 'pays', 'statut', 'chef_projet']

        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            # Tu peux aussi ajouter des widgets aux autres champs ici pour une meilleure apparence
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
