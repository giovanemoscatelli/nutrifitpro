from django.shortcuts import redirect
from django.utils import timezone
from django.urls import reverse
from django.contrib import messages

class BloqueioPagamentoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Se não estiver logado, deixa passar (o Django já pede login nas views)
        if not request.user.is_authenticated:
            return self.get_response(request)

        # 2. Se for Superusuário (Você), deixa passar sempre (não bloqueia o dono)
        #if request.user.is_superuser:
            #return self.get_response(request)

        # 3. Lista de URLs permitidas (A "Zona Segura")
        # O usuário bloqueado PRECISA acessar essas páginas para pagar ou sair
        urls_permitidas = [
            reverse('pagina_precos'), # Para pagar
            reverse('logout'),        # Para sair
            reverse('criar_pagamento'),   # O caminho para o Stripe
            reverse('pagamento_sucesso'), # O caminho da volta (para desbloquear)
            '/static/',               # Para carregar o CSS/Imagens
            '/media/',                # Para carregar fotos
            '/admin/',                # (Opcional) Se quiser deixar ele ver o admin básico
        ]

        # Verifica se a página atual está na lista permitida
        caminho_atual = request.path
        for url in urls_permitidas:
            if caminho_atual.startswith(url):
                return self.get_response(request)

        # 4. A VERIFICAÇÃO FINAL: Assinatura Vencida?
        try:
            assinatura = request.user.assinatura
            # Se a data de validade for menor que AGORA (Passado)
            if assinatura.data_validade < timezone.now():
                # Adiciona um aviso (opcional, as vezes middleware não carrega msg a tempo, mas tentamos)
                # O ideal é passar um parâmetro na URL
                return redirect(reverse('pagina_precos') + '?vencido=true')
                
        except:
            # Se o usuário não tem assinatura nenhuma criada, bloqueia também
            return redirect(reverse('pagina_precos') + '?sem_plano=true')

        return self.get_response(request)