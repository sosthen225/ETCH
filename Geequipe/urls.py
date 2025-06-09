from django.urls import include, path, reverse_lazy
from Geequipe.views import ajouter_projet, creer_equipe, enregistrer_agent, get_competences_certificats, index, liste_equipes, login_page, logout_view, modifier_agent, modifier_projet, projet_json, supprimer_agent, supprimer_projet, tabpersonels, tabprojet, voir_certificats
from django.contrib.auth import views as auth_views





urlpatterns = [
    path('', login_page, name='login'),           
    path('logout/', logout_view, name='logout'),
    path('accueil/', index, name='index'),
    path('accueil/personels/', tabpersonels, name='tabpersonels'),
    path('accueil/projets/', tabprojet, name='tabprojet'),
    path('ajouter_projet/', ajouter_projet, name='ajouter_projet'),
    path('modifier_projet/<int:id>/', modifier_projet, name='modifier_projet'),
    path('supprimer_projet/<int:id>/', supprimer_projet, name='supprimer_projet'),

    #path('projets/<int:projet_id>/json/', projet_json, name='projet_json'),
    #path('projets/<int:id>/modifier/', modifier_projet, name='modifier_projet')

   #path('api/competences-certificats/',get_competences_certificats, name='get_competences_certificats'),
    path('api/enregistrer-agent/', enregistrer_agent, name='enregistrer_agent'),
    path('modifier_agent/<int:id>/', modifier_agent, name='modifier_agent'),
    path('agents/supprimer/<int:agent_id>/',supprimer_agent, name='supprimer_agent'),
    

    path('details_certificat/<int:personnel_id>/', voir_certificats, name='voir_certificats'),
    
    path('creer_equipe/',creer_equipe, name='creer_equipe'),
    path('liste_equipes/',liste_equipes, name='liste_equipes'),
    

]
