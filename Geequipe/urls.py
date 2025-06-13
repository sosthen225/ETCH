from django.urls import include, path, reverse_lazy
from ETCH import settings
from Geequipe.views import affecter_equipe, ajouter_projet, creer_equipe, creer_mobilisation, enregistrer_agent, equipes_disponibles, get_competences_certificats, index, liste_equipes, login_page, logout_view, mobiliser_equipes, modifier_agent, modifier_projet, organiser_mobilisation, projet_json, projets_disponibles, search_results, supprimer_affectation, supprimer_agent, supprimer_projet, tabpersonels, tabprojet, voir_certificats
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static




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
    path('/accueil/personels/modifier_agent/<int:agent_id>/', modifier_agent, name='modifier_agent'),
    path('agents/supprimer/<int:agent_id>/',supprimer_agent, name='supprimer_agent'),
    

    path('details_certificat/<int:personnel_id>/', voir_certificats, name='voir_certificats'),
    
    path('creer_equipe/',creer_equipe, name='creer_equipe'),
    path('liste_equipes/',liste_equipes, name='liste_equipes'),
   
    path('modifer_equipe/<int:id>/', affecter_equipe, name='modifier_equipe'),
    path('supprimer_equipe/<int:id>/', affecter_equipe, name='supprimer_equipe'),
    

    path('organiser_mobilisation/',organiser_mobilisation, name='organiser_mobilisation'),
    path('creer_mobilisation/<int:projet_id>/',creer_mobilisation, name='creer_mobilisation'),
         
    path('mobiliser_equipes/<int:projet_id>/', mobiliser_equipes, name='mobiliser_equipes'),

    path('ajax/equipes_disponibles/', equipes_disponibles, name='equipes_disponibles'),
    path('ajax/projets_disponibles/', projets_disponibles, name='projets_disponibles'),
    path('affecter_equipe/', affecter_equipe, name='affecter_equipe'),
    path('supprimer-affectation/<int:affectation_id>/', supprimer_affectation, name='supprimer_affectation'),


    path('search/', search_results, name='search_results'),

]
