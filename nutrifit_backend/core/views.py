from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse # <--- IMPORTANTE: Novo import para o App
from .models import PlanoAlimentar, Refeicao, PlanoTreino, Cliente, FichaAnamnese, ConfiguracaoAnamnese, Notificacao

# --- VIEW 1: ANAMNESE PÚBLICA ---
def anamnese_publica(request, uuid_link):
    configuracao = get_object_or_404(ConfiguracaoAnamnese, codigo_link=uuid_link)
    profissional = configuracao.profissional

    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        data_nascimento = request.POST.get('data_nascimento')
        genero = request.POST.get('genero')

        if User.objects.filter(username=email).exists() or Cliente.objects.filter(email=email).exists():
            return render(request, 'core/form_anamnese.html', {
                'erro': 'E-mail já cadastrado!',
                'config': configuracao,
                'profissional': profissional
            })

        try:
            User.objects.create_user(username=email, email=email, password=senha)
            
            novo_cliente = Cliente.objects.create(
                nome=nome,
                email=email,
                data_nascimento=data_nascimento,
                genero=genero
            )

            FichaAnamnese.objects.create(
                cliente=novo_cliente,
                ocupacao=request.POST.get('ocupacao'),
                rotina_trabalho=request.POST.get('rotina_trabalho'),
                composicao_familiar=request.POST.get('composicao_familiar'),
                responsavel_compras=request.POST.get('responsavel_compras'),
                problema_cardiaco='problema_cardiaco' in request.POST,
                dor_peito_atividade='dor_peito_atividade' in request.POST,
                dor_peito_repouso='dor_peito_repouso' in request.POST,
                tontura_perda_consciencia='tontura_perda_consciencia' in request.POST,
                problema_osseo='problema_osseo' in request.POST,
                medicamento_pressao='medicamento_pressao' in request.POST,
                historico_lesoes=request.POST.get('historico_lesoes'),
                horas_sono=request.POST.get('horas_sono') or 0,
                qualidade_sono=request.POST.get('qualidade_sono'),
                ronca_apneia='ronca_apneia' in request.POST,
                higiene_sono_telas='higiene_sono_telas' in request.POST,
                objetivo=request.POST.get('objetivo'),
                efeito_sanfona='efeito_sanfona' in request.POST,
                dietas_previas=request.POST.get('dietas_previas'),
                consumo_agua=request.POST.get('consumo_agua'),
                intestino_preso='intestino_preso' in request.POST,
                gases_estufamento='gases_estufamento' in request.POST,
                azia_refluxo='azia_refluxo' in request.POST,
                suplementos_farmacos=request.POST.get('suplementos_farmacos'),
                fadiga_matinal='fadiga_matinal' in request.POST,
                queda_energia_tarde='queda_energia_tarde' in request.POST,
                intolerancia_frio='intolerancia_frio' in request.POST,
                queda_cabelo='queda_cabelo' in request.POST,
                desejo_sal_doce='desejo_sal_doce' in request.POST,
                libido_baixa='libido_baixa' in request.POST,
                forca_reduzida='forca_reduzida' in request.POST,
                ciclo_menstrual_regular='ciclo_menstrual_regular' in request.POST,
                amenorreia='amenorreia' in request.POST,
                anticoncepcional=request.POST.get('anticoncepcional'),
                motivacao_principal=request.POST.get('motivacao_principal'),
                vergonha_corpo=request.POST.get('vergonha_corpo'),
                tempo_treino=request.POST.get('tempo_treino'),
                disponibilidade_treino=request.POST.get('disponibilidade_treino'),
                exercicios_odiados=request.POST.get('exercicios_odiados'),
                observacoes_finais=request.POST.get('observacoes_finais')
            )

            return redirect('login')
            
        except Exception as e:
            return render(request, 'core/form_anamnese.html', {
                'erro': f'Erro ao salvar ficha: {e}',
                'config': configuracao,
                'profissional': profissional
            })

    return render(request, 'core/form_anamnese.html', {
        'config': configuracao, 
        'profissional': profissional
    })


# --- VIEW 2: PAINEL DO CLIENTE ---
@login_required
def visualizar_dieta(request):
    usuario_logado = request.user
    
    try:
        cliente = Cliente.objects.get(email=usuario_logado.email)
        plano_alimentar = PlanoAlimentar.objects.filter(cliente=cliente).last()
        treinos = PlanoTreino.objects.filter(cliente=cliente)
        
    except Cliente.DoesNotExist:
        plano_alimentar = None
        treinos = []
        
        if usuario_logado.is_superuser:
            plano_alimentar = PlanoAlimentar.objects.last()
            if plano_alimentar:
                treinos = PlanoTreino.objects.filter(cliente=plano_alimentar.cliente)

    if plano_alimentar:
        refeicoes = Refeicao.objects.filter(plano_alimentar=plano_alimentar).order_by('horario')
    else:
        refeicoes = []

    # NOVIDADE: Buscando Notificações para o Sino
    notificacoes = Notificacao.objects.filter(destinatario=usuario_logado, lida=False)
    qtd_notificacoes = notificacoes.count()

    contexto = {
        'plano': plano_alimentar,
        'refeicoes': refeicoes,
        'treinos': treinos,
        'notificacoes': notificacoes,
        'qtd_notificacoes': qtd_notificacoes
    }
    return render(request, 'core/relatorio_dieta.html', contexto)


# --- VIEW 3: MANIFESTO DO APP (PWA) ---
# Essa função serve o arquivo JSON que transforma o site em App
def manifest_view(request):
    return JsonResponse({
        "name": "NutriFit Pro",
        "short_name": "NutriFit",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#2c3e50",
        "icons": [
            {
                "src": "/static/core/icon.png", 
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    })