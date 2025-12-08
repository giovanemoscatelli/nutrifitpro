# Calculadora de IMC do NutriFit Pro
# Autor: Giovane Moscatelli

print("--- Bem-vindo à Calculadora NutriFit ---")

# 1. Coleta de Dados Completa (Input)
# O comando input pega o que o usuário digita, mas vem como texto.
# O comando float converte esse texto em número decimal (com ponto).
# Vamos pedir o gênero. O .lower() garante que 'Homem' vire 'homem'
genero = input("Qual seu gênero biológico? (homem/mulher): ").strip().lower()

peso = float(input("Digite seu peso em Kg (ex: 70.5): "))
altura = float(input("Digite sua altura em Metros (ex: 1.75): "))
cintura = float(input("Digite a circunferência de sua cintura em centimetros (cm):"))
quadril = float(input("Digite a circunferência de seu quadril em centimetros (cm):")) #Nova variável!

# 2. Processamento (A Matemática)
# A fórmula é Peso dividido pela Altura ao quadrado
imc = peso / (altura * altura)

#Cálculo da RQC (Relação Cintura-Quadril)
#Esse índice diz se a gordura está perigosamente na barriga
rcq = cintura / quadril

print(f"\n--- RESULTADOS ---")
print(f"IMC: {imc:.2f}")
print(f"RCQ: {rcq:.2f}")

# 3. A LÓGICA INTELIGENTE (Separada por Gênero)

# --- CAMINHO DOS HOMENS ---
if genero == "homem":
    # Homens têm risco alto se RCQ > 0.90
    limite_rcq = 0.90
    print("Analisando dados para o padrão MASCULINO...")

    if imc > 25 and rcq < limite_rcq:
        print("DIAGNÓSTICO: IMC Alto, mas proporção Cintura/Quadril saudavel.")
        print("Provável físico atlético ou 'Falso Gordo'.")
    elif imc > 25 and rcq >= limite_rcq:
        print("DIAGNÓSTICO: Obesidade com risco cardiovascular (gordura abdominal).")
    else:
        print("DIAGNÓSTICO: Peso e medidas dentro do padrão.")    

# --- CAMINHO DAS MULHERES ---
elif genero == "mulher":
    # Mulheres têm risco alto se RCQ > 0.85 (elas acumulam mais gordura no quadril naturalmente)
    limite_rcq = 0.85
    print("Analisando dados para o padrão FEMININO...")

    if imc >25 and rcq < limite_rcq:
        print("DIAGNÓSTICO: Curvas acentuadas (padrão 'Pera'), mas baixo risco visceral.")
        print("Provável ganho de massa ou gordura periférica (menos perigosa).")
    elif imc > 25 and rcq >= limite_rcq:
        print("DIAGNÓSTICO: Obesidade com risco (gordura abdominal).")   
    else:
        print("DIAGNÓSTICO: Peso e medidas dentro do padrão.")

# --- CAMINHO DE ERRO (Se digitar "alienígena" ou errar a digitação)---
else:
    print("Erro: Gênero não reconhecido. Por favor digite 'homem' ou 'mulher'.")
