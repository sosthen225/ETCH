from django.urls import include, path, reverse_lazy
from Geequipe.views import ajouter_projet, index, login_page, logout_view, tabpersonels, tabprojet
from django.contrib.auth import views as auth_views





urlpatterns = [
    path('', login_page, name='login'),           
    path('logout/', logout_view, name='logout'),
    path('accueil/', index, name='index'),
    path('accueil/personels/', tabpersonels, name='tabpersonels'),
    path('accueil/projets/', tabprojet, name='tabprojet'),
    path('ajouter_projet/', ajouter_projet, name='ajouter_projet'),
    # path('modifier-projet/<int:projet_id>/', modifier_projet, name='modifier_projet'),
    # path('supprimer-projet/<int:projet_id>/', supprimer_projet, name='supprimer_projet'),
    
    
]
