from django.urls import include, path, reverse_lazy
from Geequipe.views import ajouter_projet, index, login_page, logout_view, modifier_projet, projet_json, supprimer_projet, tabpersonels, tabprojet
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

    
    
    
]
