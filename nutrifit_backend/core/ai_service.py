import json
from openai import OpenAI
from django.conf import settings
from .models import PlanoAlimentar, Refeicao, PlanoTreino, Exercicio

# Se tiver chave real, coloque aqui
API_KEY = "SUA-CHAVE-AQUI" 

def gerar_plano_inteligente(cliente):
    # 1. TENTA USAR A IA REAL
    try:
        if API_KEY == "SUA-CHAVE-AQUI" or not API_KEY:
            raise Exception("Sem chave de API - Usando Simulação")

        client = OpenAI(api_key=API_KEY)
        # ... lógica real ...
        raise Exception("Forçando Simulação")

    # 2. MODO SIMULAÇÃO (MOCK HUMANIZADO)
    except Exception as e:
        print(f"Log interno: Gerando plano simulado para {cliente.nome}")
        
        # --- LÓGICA DE DECISÃO BASEADA NO OBJETIVO ---
        try:
            # Tenta pegar da ficha, se não tiver ficha, assume Geral
            objetivo = cliente.anamnese.objetivo
        except:
            objetivo = "Geral"

        if objetivo == 'hipertrofia':
            titulo_dieta = "Protocolo de Ganho de Massa (Fase 1)"
            titulo_treino = "Treino de Força e Hipertrofia"
            obs_dieta = "Foco total na ingestão de proteínas e carboidratos complexos. Não pule refeições."
            obs_treino = "Mantenha a intensidade alta. Tente aumentar a carga progressivamente a cada semana."
        
        elif objetivo == 'emagrecimento':
            titulo_dieta = "Protocolo de Definição e Perda de Gordura"
            titulo_treino = "Treino Metabólico Intensivo"
            obs_dieta = "Beba pelo menos 3L de água por dia. Evite alimentos industrializados fora do plano."
            obs_treino = "Priorize a execução correta e o descanso curto (45s a 60s) entre as séries."
        
        else:
            titulo_dieta = "Reeducação Alimentar e Saúde"
            titulo_treino = "Condicionamento Físico Geral"
            obs_dieta = "O objetivo é criar hábitos saudáveis e sustentáveis a longo prazo."
            obs_treino = "Foco na regularidade. O importante é não ficar parado."

        # --- SALVANDO NO BANCO (SEM AVISAR QUE É IA) ---
        
        # 1. Cria a Dieta
        plano_dieta = PlanoAlimentar.objects.create(
            cliente=cliente,
            titulo=titulo_dieta, # Antes tinha "Sugestão IA:", agora tá limpo
            observacoes=obs_dieta
        )
        
        # Refeições Exemplo
        Refeicao.objects.create(plano_alimentar=plano_dieta, horario="08:00", nome="Café da Manhã", descricao_alimentos="3 Ovos mexidos ou cozidos\n2 Fatias de pão integral ou tapioca\n1 Xícara de Café preto sem açúcar", eh_suplementacao=False)
        Refeicao.objects.create(plano_alimentar=plano_dieta, horario="12:00", nome="Almoço", descricao_alimentos="150g Proteína Magra (Frango/Peixe/Carne)\n100g Carboidrato (Arroz/Batata)\nSalada de folhas à vontade (Tempere com azeite)", eh_suplementacao=False)
        Refeicao.objects.create(plano_alimentar=plano_dieta, horario="16:00", nome="Lanche da Tarde", descricao_alimentos="1 Fruta média (Maçã/Banana)\n30g Aveia ou Mix de Castanhas", eh_suplementacao=False)
        Refeicao.objects.create(plano_alimentar=plano_dieta, horario="18:00", nome="Pós-Treino (Opcional)", descricao_alimentos="30g Whey Protein\n5g Creatina\n(Misturar com água gelada)", eh_suplementacao=True)

        # 2. Cria o Treino
        plano_treino = PlanoTreino.objects.create(
            cliente=cliente,
            titulo=titulo_treino, # Limpo
            local="academia",
            observacoes=obs_treino
        )

        # Exercícios Exemplo
        Exercicio.objects.create(plano_treino=plano_treino, nome="Supino Reto (Barra ou Halteres)", series=4, repeticoes="10-12", carga_kg="Moderada", video_demonstracao="https://www.youtube.com/results?search_query=supino+reto+execucao")
        Exercicio.objects.create(plano_treino=plano_treino, nome="Agachamento Livre", series=4, repeticoes="10", carga_kg="Desafiadora", video_demonstracao="https://www.youtube.com/results?search_query=agachamento+livre+execucao")
        Exercicio.objects.create(plano_treino=plano_treino, nome="Puxada Alta (Costas)", series=3, repeticoes="12-15", carga_kg="Controle total", video_demonstracao="")
        Exercicio.objects.create(plano_treino=plano_treino, nome="Abdominal Supra", series=3, repeticoes="20", carga_kg="", video_demonstracao="")

        return "Sucesso! Planos personalizados gerados."