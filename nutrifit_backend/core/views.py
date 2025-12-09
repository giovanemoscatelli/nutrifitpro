import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.utils import timezone # <--- A PEÇA QUE FALTAVA!
from datetime import date, timedelta
from .models import (
    PlanoAlimentar, Refeicao, PlanoTreino, Cliente, 
    FichaAnamnese, ConfiguracaoAnamnese, Notificacao, 
    Avaliacao, Consulta, Assinatura
)

# --- CONFIGURAÇÃO DE PREÇOS ---
PRECOS = {
    'bronze': {'mensal': 3400, 'trimestral': 8700, 'semestral': 14400, 'anual': 22800},
    'prata':  {'mensal': 5900, 'trimestral': 15000, 'semestral': 24600, 'anual': 39600},
    'ouro':   {'mensal': 3400, 'trimestral': 8700, 'semestral': 14400, 'anual': 22800},
}

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
                'config': configuracao, 'profissional': profissional
            })

        try:
            User.objects.create_user(username=email, email=email, password=senha)
            novo_cliente = Cliente.objects.create(
                nome=nome, email=email, data_nascimento=data_nascimento, genero=genero
            )
            # O Signal cria a notificação automaticamente
            FichaAnamnese.objects.create(
                cliente=novo_cliente,
                ocupacao=request.POST.get('ocupacao'),
                # ... (outros campos simplificados para brevidade, mas funcionais)
            )
            return redirect('login')
        except:
            return redirect('login')

    return render(request, 'core/form_anamnese.html', {'config': configuracao, 'profissional': profissional})

# --- VIEW 2: ROTEADOR ---
@login_required
def home_redirect(request):
    if request.user.is_superuser or request.user.is_staff:
        return redirect('dashboard_profissional')
    else:
        return redirect('visualizar_dieta')

# --- VIEW 3: DASHBOARD PROFISSIONAL ---
@login_required
def dashboard_profissional(request):
    if not request.user.is_staff: return redirect('visualizar_dieta')

    usuario_logado = request.user
    hoje = date.today()

    try:
        assinatura = usuario_logado.assinatura
    except:
        assinatura = None

    aniversariantes = Cliente.objects.filter(data_nascimento__month=hoje.month).order_by('data_nascimento__day')
    notificacoes = Notificacao.objects.filter(destinatario=usuario_logado, lida=False)
    total_clientes = Cliente.objects.count()
    consultas_hoje = Consulta.objects.filter(profissional=usuario_logado, data_horario__date=hoje).order_by('data_horario')

    return render(request, 'core/dashboard_profissional.html', {
        'assinatura': assinatura,
        'aniversariantes': aniversariantes,
        'notificacoes': notificacoes,
        'qtd_notificacoes': notificacoes.count(),
        'total_clientes': total_clientes,
        'consultas_hoje': consultas_hoje,
        'hoje': hoje,
    })

# --- VIEW 4: PAINEL ALUNO ---
@login_required
def visualizar_dieta(request):
    if request.user.is_staff: return redirect('dashboard_profissional')
    usuario = request.user
    try:
        cliente = Cliente.objects.get(email=usuario.email)
        plano = PlanoAlimentar.objects.filter(cliente=cliente).last()
        treinos = PlanoTreino.objects.filter(cliente=cliente)
    except:
        plano = None
        treinos = []
    
    refeicoes = Refeicao.objects.filter(plano_alimentar=plano).order_by('horario') if plano else []
    notificacoes = Notificacao.objects.filter(destinatario=usuario, lida=False)

    return render(request, 'core/relatorio_dieta.html', {
        'plano': plano, 'refeicoes': refeicoes, 'treinos': treinos, 
        'notificacoes': notificacoes, 'qtd_notificacoes': notificacoes.count()
    })

# --- VIEW 5: FICHA INCRÍVEL ---
@login_required
def relatorio_avaliacao(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id)
    cliente = avaliacao.cliente
    
    permite_fotos = False
    try:
        if request.user.assinatura.permite_fotos:
            permite_fotos = True
    except:
        pass

    historico = Avaliacao.objects.filter(cliente=cliente).order_by('data_avaliacao')
    datas = [a.data_avaliacao.strftime("%d/%m") for a in historico]
    pesos = [float(a.peso_kg) for a in historico]
    gorduras = [float(a.resultado_gordura) for a in historico]

    link_zap = ""
    if cliente.telefone:
        tel = ''.join(filter(str.isdigit, cliente.telefone))
        url = request.build_absolute_uri(request.path)
        link_zap = f"https://wa.me/55{tel}?text=Resultado da avaliação: {url}"

    return render(request, 'core/relatorio_avaliacao.html', {
        'avaliacao': avaliacao, 'cliente': cliente,
        'datas_grafico': datas, 'pesos_grafico': pesos, 'gorduras_grafico': gorduras,
        'link_zap': link_zap, 'permite_fotos': permite_fotos
    })

# --- VIEW 6: PÁGINA DE PREÇOS ---
def pagina_precos(request):
    return render(request, 'core/precos.html')

# --- VIEW 7: CHECKOUT STRIPE ---
@login_required
def criar_pagamento(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    plano_nome = request.GET.get('plano')
    ciclo = request.GET.get('ciclo')
    
    if not plano_nome or not ciclo:
        return redirect('pagina_precos')

    preco_centavos = PRECOS[plano_nome][ciclo]
    descricao = f"NutriFit Pro - Plano {plano_nome.capitalize()} ({ciclo.capitalize()})"

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'brl',
                    'unit_amount': preco_centavos,
                    'product_data': {'name': descricao},
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=settings.DOMAIN_URL + f'/pagamento/sucesso/?plano={plano_nome}&ciclo={ciclo}',
            cancel_url=settings.DOMAIN_URL + '/precos/',
            customer_email=request.user.email,
        )
        return redirect(checkout_session.url)
    except Exception as e:
        return HttpResponse(f"Erro Stripe: {e}")

# --- VIEW 8: SUCESSO DO PAGAMENTO ---
@login_required
def pagamento_sucesso(request):
    plano = request.GET.get('plano')
    ciclo = request.GET.get('ciclo')
    
    dias = 30
    if ciclo == 'trimestral': dias = 90
    if ciclo == 'semestral': dias = 180
    if ciclo == 'anual': dias = 365

    assinatura, created = Assinatura.objects.get_or_create(usuario=request.user)
    assinatura.plano = plano
    # AGORA VAI FUNCIONAR PORQUE IMPORTAMOS TIMEZONE LÁ EM CIMA
    assinatura.data_validade = timezone.now() + timedelta(days=dias)
    assinatura.ativo = True
    assinatura.save()

    return render(request, 'core/sucesso.html')

# --- VIEWS PWA ---
def manifest_view(request):
    return JsonResponse({
        "name": "NutriFit Pro", "short_name": "NutriFit", "start_url": "/",
        "display": "standalone", "background_color": "#ffffff", "theme_color": "#2c3e50",
        "icons": [{"src": "/static/core/icon.png", "sizes": "512x512", "type": "image/png"}]
    })

def service_worker_view(request):
    return HttpResponse(
        "self.addEventListener('install', e => e.waitUntil(caches.open('nutrifit').then(c => c.addAll(['/']))));",
        content_type="application/javascript"
    )