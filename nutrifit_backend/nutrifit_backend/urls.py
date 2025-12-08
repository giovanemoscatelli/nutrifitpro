from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
# Adicionamos manifest_view no import
from core.views import visualizar_dieta, anamnese_publica, manifest_view 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('anamnese/convite/<uuid:uuid_link>/', anamnese_publica, name='anamnese_publica'),

    # O endereço do arquivo de configuração do App
    path('manifest.json', manifest_view, name='manifest'),

    path('', visualizar_dieta, name='home'), 
]