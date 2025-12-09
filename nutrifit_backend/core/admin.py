from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    Cliente, FichaAnamnese, Avaliacao, 
    PlanoAlimentar, Refeicao, PlanoTreino, 
    Exercicio, ConfiguracaoAnamnese, Notificacao,
    Consulta, Assinatura # <--- NOVO
)

try:
    from .ai_service import gerar_plano_inteligente
except ImportError:
    gerar_plano_inteligente = None

# AÇÃO IA
def gerar_plano_ia_action(modeladmin, request, queryset):
    if not gerar_plano_inteligente:
        messages.error(request, "Serviço de IA indisponível.")
        return
    for cliente in queryset:
        resultado = gerar_plano_inteligente(cliente)
        if "Sucesso" in resultado:
            messages.success(request, f"IA: Planos gerados para {cliente.nome}!")
        else:
            messages.error(request, f"Erro {cliente.nome}: {resultado}")
gerar_plano_ia_action.short_description = "🤖 Gerar Treino e Dieta com IA"

# CLIENTE + FICHA
class FichaAnamneseInline(admin.StackedInline):
    model = FichaAnamnese
    can_delete = False
    verbose_name_plural = 'Prontuário / Anamnese'
    fk_name = 'cliente'

class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'genero', 'telefone')
    search_fields = ('nome', 'email')
    inlines = [FichaAnamneseInline]
    actions = [gerar_plano_ia_action]

# AVALIAÇÃO + BOTÃO
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'data_avaliacao', 'resultado_gordura', 'botao_ficha')
    def botao_ficha(self, obj):
        url = reverse('relatorio_avaliacao', args=[obj.id])
        return format_html(
            '<a class="button" href="{}" target="_blank" style="background:#2ecc71; color:white; padding:5px 10px; border-radius:5px; text-decoration:none;">📄 Ver Ficha</a>',
            url
        )
    botao_ficha.short_description = 'Relatório'

# AGENDA
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ('data_horario', 'cliente', 'status', 'botao_zap')
    list_filter = ('status', 'data_horario')
    def botao_zap(self, obj):
        if not obj.cliente.telefone: return "-"
        data = obj.data_horario.strftime('%d/%m às %H:%M')
        msg = f"Olá {obj.cliente.nome}, lembrete da consulta dia {data}. Confirmado?"
        tel = ''.join(filter(str.isdigit, obj.cliente.telefone))
        link = f"https://wa.me/55{tel}?text={msg}"
        return format_html('<a class="button" href="{}" target="_blank" style="background:#25D366; color:white; padding:3px 8px; border-radius:4px;">📱 Avisar</a>', link)
    botao_zap.short_description = "WhatsApp"

# ASSINATURA (NOVIDADE)
class AssinaturaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'plano', 'data_validade', 'ativo')
    list_filter = ('plano', 'ativo')

# REGISTROS
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Avaliacao, AvaliacaoAdmin)
admin.site.register(Consulta, ConsultaAdmin)
admin.site.register(Assinatura, AssinaturaAdmin) # <--- AQUI
admin.site.register(ConfiguracaoAnamnese)
admin.site.register(FichaAnamnese)
admin.site.register(PlanoAlimentar)
admin.site.register(Refeicao)
admin.site.register(PlanoTreino)
admin.site.register(Exercicio)
admin.site.register(Notificacao)