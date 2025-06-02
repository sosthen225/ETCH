from django.urls import include, path, reverse_lazy
from Geequipe.views import index, login_page, logout_view, tabpersonels, tabprojet
from django.contrib.auth import views as auth_views





urlpatterns = [
    path('', login_page, name='login'),           
    path('logout/', logout_view, name='logout'),
    path('accueil/', index, name='index'),
    path('accueil/personels/', tabpersonels, name='tabpersonels'),
    path('accueil/projets/', tabprojet, name='tabprojet'),
    
    
]
