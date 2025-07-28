from django.urls import include, path, reverse_lazy
from ETCH import settings
from Geequipe.views import affecter_equipe, ajouter_projet, ajouter_taches, assign_tasks_to_team, changer_statut_activite, changer_statut_personnel, creer_equipe, creer_mobilisation, enregistrer_agent, equipes_disponibles, exporter_projet_excel, get_personnels_by_role,  index, liste_activites, liste_equipes, liste_mobilisations, login_page, logout_view, mobiliser_equipes, modifier_agent, modifier_equipe, modifier_projet, modifier_statut_projet, organiser_mobilisation, projets_disponibles, resume_mobilisation, search_results, supprimer_activite, supprimer_affectation, supprimer_agent, supprimer_equipe, supprimer_projet, supprimer_tache, tabpersonels, tabprojet, voir_certificats, voir_taches
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
    path('projets/<int:projet_id>/',ajouter_taches, name='ajouter_taches'),
    path('activites/<int:activite_id>/supprimer/', supprimer_activite, name='supprimer_activite'),
   

    #path('projets/<int:projet_id>/json/', projet_json, name='projet_json'),
    #path('projets/<int:id>/modifier/', modifier_projet, name='modifier_projet')

   #path('api/competences-certificats/',get_competences_certificats, name='get_competences_certificats'),
    path('api/enregistrer-agent/', enregistrer_agent, name='enregistrer_agent'),
    path('/accueil/personels/modifier_agent/<int:agent_id>/', modifier_agent, name='modifier_agent'),
    path('agents/supprimer/<int:agent_id>/',supprimer_agent, name='supprimer_agent'),
    path('projets/<int:agent_id>/changer-statut/',changer_statut_personnel, name='changer_statut_agent'),
    path('modifier_statut/<int:projet_id>/',modifier_statut_projet, name='modifier_statut_projet'),
    path('exporter_projet/<int:projet_id>/', exporter_projet_excel, name='exporter_projet_excel'),
    path('details_certificat/<int:personnel_id>/', voir_certificats, name='voir_certificats'),
    
    path('creer_equipe/',creer_equipe, name='creer_equipe'),
    path('liste_equipes/',liste_equipes, name='liste_equipes'),
   
    path('modifer_equipe/<int:equipe_id>/', modifier_equipe, name='modifier_equipe'),
    path('supprimer_equipe/<int:equipe_id>/', supprimer_equipe, name='supprimer_equipe'),
    

    path('organiser_mobilisation/',organiser_mobilisation, name='organiser_mobilisation'),
    path('creer_mobilisation/<int:projet_id>/',creer_mobilisation, name='creer_mobilisation'),
         
    path('mobiliser_equipes/<int:projet_id>/', mobiliser_equipes, name='mobiliser_equipes'),
    path('resume_mobilisation/<int:mobilisation_id>/', resume_mobilisation, name='resume_mobilisation'),
    path('liste_mobilisations/', liste_mobilisations, name='liste_mobilisations'),

    path('activites/', liste_activites, name='liste_activites'),
    path('activites/<int:activite_id>/changer-statut/',changer_statut_activite, name='changer_statut_activite'),
    #path('affectation/allouer-taches/<int:projet_id>/<int:equipe_id>/', allouer_taches, name='allouer_taches'),
     path('projet/<int:projet_id>/taches/', voir_taches, name='voir_taches'),



    path('ajax/equipes_disponibles/', equipes_disponibles, name='equipes_disponibles'),
    path('ajax/projets_disponibles/', projets_disponibles, name='projets_disponibles'),
    path('affecter_equipe/', affecter_equipe, name='affecter_equipe'),
    path('supprimer-affectation/<int:affectation_id>/', supprimer_affectation, name='supprimer_affectation'),

    path('change-password/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change_form.html'), name='password_change'),
    path('change-password/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
   


    path('affectation/<int:affectation_id>/assigner-taches/', assign_tasks_to_team, name='assign_tasks_to_team'),

    path('search/', search_results, name='search_results'),
    path('api/get-personnels/', get_personnels_by_role, name='get_personnels_by_role'),

    path('tache/supprimer/<int:tache_id>/', supprimer_tache, name='supprimer_tache'),

   


  
    
    # Gestion du mot de passe oublié
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt'
         ),
         name='password_reset'),

    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),

    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),


]
