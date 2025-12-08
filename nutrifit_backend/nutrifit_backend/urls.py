from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core.views import (
    home_redirect, anamnese_publica, 
    manifest_view, service_worker_view
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('anamnese/convite/<uuid:uuid_link>/', anamnese_publica, name='anamnese_publica'),

    # PWA
    path('manifest.json', manifest_view, name='manifest'),
    path('sw.js', service_worker_view, name='service_worker'), # <--- NOVO (Para instalar offline)

    # Rota Principal (O Roteador Inteligente)
    path('', home_redirect, name='home'), 
]