from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from core.views import (
    dashboard_profissional, visualizar_dieta, 
    anamnese_publica, manifest_view, service_worker_view,
    home_redirect, relatorio_avaliacao, pagina_precos, criar_pagamento, pagamento_sucesso # <--- Adicionei pagina_precos aqui
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('anamnese/convite/<uuid:uuid_link>/', anamnese_publica, name='anamnese_publica'),
    path('manifest.json', manifest_view, name='manifest'),
    path('sw.js', service_worker_view, name='sw'),

    path('dashboard/', dashboard_profissional, name='dashboard_profissional'),
    path('aluno/', visualizar_dieta, name='visualizar_dieta'),
    path('avaliacao/<int:avaliacao_id>/', relatorio_avaliacao, name='relatorio_avaliacao'),
    
    # Rota nova de Preços
    path('precos/', pagina_precos, name='pagina_precos'),

    path('', home_redirect, name='home'),
    path('pagamento/criar/', criar_pagamento, name='criar_pagamento'),
    path('pagamento/sucesso/', pagamento_sucesso, name='pagamento_sucesso'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)