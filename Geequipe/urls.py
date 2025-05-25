from django.urls import path
from Geequipe.views import index, login_page, tabpersonels



urlpatterns = [
    path('', login_page, name='login'),
    path('accueil/',index, name='index'),
    path('personels/',tabpersonels, name='tabpersonels'),
]