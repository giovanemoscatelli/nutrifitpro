from django.contrib import admin
from django.contrib import messages # Importante para mostrar avisos de Sucesso/Erro
from .models import (
    Cliente, FichaAnamnese, Avaliacao, 
    PlanoAlimentar, Refeicao, PlanoTreino, 
    Exercicio, ConfiguracaoAnamnese
)
# Importamos a função de IA que criamos no outro arquivo
# (Se der erro aqui, verifique se o arquivo ai_service.py foi criado na pasta core)
try:
    from .ai_service import gerar_plano_inteligente
except ImportError:
    # Caso você ainda não tenha criado o arquivo, evita que o site quebre
    gerar_plano_inteligente = None

# --- AÇÃO PERSONALIZADA (O BOTÃO DA IA) ---
def gerar_plano_ia_action(modeladmin, request, queryset):
    if not gerar_plano_inteligente:
        messages.error(request, "O serviço de IA (ai_service.py) não foi encontrado ou está com erro.")
        return

    for cliente in queryset:
        # Chama a função que criamos no ai_service.py
        resultado = gerar_plano_inteligente(cliente)
        
        if "Sucesso" in resultado:
            messages.success(request, f"IA: Planos gerados para {cliente.nome} com sucesso!")
        else:
            messages.error(request, f"Erro ao gerar para {cliente.nome}: {resultado}")

# Nome bonito que vai aparecer no menu "Action"
gerar_plano_ia_action.short_description = "🤖 Gerar Treino e Dieta com IA"


# --- CONFIGURAÇÃO DO CLIENTE (COM FICHA E BOTÃO) ---
class FichaAnamneseInline(admin.StackedInline):
    model = FichaAnamnese
    can_delete = False
    verbose_name_plural = 'Prontuário / Anamnese'
    fk_name = 'cliente'

class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'genero', 'data_nascimento')
    search_fields = ('nome', 'email')
    
    # Adiciona a ficha dentro do cliente
    inlines = [FichaAnamneseInline]
    
    # ADICIONA O BOTÃO DA IA NO MENU DE AÇÕES
    actions = [gerar_plano_ia_action]


# --- REGISTROS ---
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(ConfiguracaoAnamnese)
admin.site.register(FichaAnamnese) # Opcional, já aparece dentro do cliente
admin.site.register(Avaliacao)
admin.site.register(PlanoAlimentar)
admin.site.register(Refeicao)
admin.site.register(PlanoTreino)
admin.site.register(Exercicio)