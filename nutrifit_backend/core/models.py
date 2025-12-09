from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
import math
import uuid

# --- 1. CLIENTE (A BASE DE TUDO) ---
class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True, help_text="Apenas números com DDD (ex: 11999999999)")
    data_nascimento = models.DateField()
    
    GENERO_CHOICES = [
        ('homem', 'Homem'),
        ('mulher', 'Mulher'),
    ]
    genero = models.CharField(max_length=10, choices=GENERO_CHOICES)
    observacoes = models.TextField(blank=True, null=True, verbose_name="Anamnese / Observações")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return self.nome

# --- 2. AVALIAÇÃO FÍSICA (Depende de Cliente) ---
class Avaliacao(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    data_avaliacao = models.DateTimeField(auto_now_add=True)
    
    peso_kg = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Peso (Kg)")
    altura_m = models.DecimalField(max_digits=3, decimal_places=2, verbose_name="Altura (m)")
    cintura_cm = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Cintura (cm)")
    pescoco_cm = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Pescoço (cm)")
    quadril_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Quadril (cm)")

    foto_frente = models.ImageField(upload_to='avaliacoes/', blank=True, null=True, verbose_name="Foto Frente")
    foto_costas = models.ImageField(upload_to='avaliacoes/', blank=True, null=True, verbose_name="Foto Costas")
    foto_perfil = models.ImageField(upload_to='avaliacoes/', blank=True, null=True, verbose_name="Foto Perfil")

    resultado_imc = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    resultado_gordura = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    classificacao = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = "Avaliação Física"
        verbose_name_plural = "Avaliações Físicas"

    def __str__(self):
        data_formatada = self.data_avaliacao.strftime('%d/%m/%Y')
        if self.resultado_imc:
            return f"{self.cliente.nome} ({data_formatada}) - BF: {self.resultado_gordura}%"
        return f"{self.cliente.nome} ({data_formatada})"

    def save(self, *args, **kwargs):
        try:
            imc_bruto = float(self.peso_kg) / (float(self.altura_m) * float(self.altura_m))
            self.resultado_imc = round(imc_bruto, 2)
        except:
            self.resultado_imc = 0
        
        try:
            altura_cm = float(self.altura_m) * 100
            cintura = float(self.cintura_cm)
            pescoco = float(self.pescoco_cm)
            gordura_calc = 0
            if self.cliente.genero == 'homem':
                gordura_calc = 495 / (1.0324 - 0.19077 * math.log10(cintura - pescoco) + 0.15456 * math.log10(altura_cm)) - 450
            elif self.cliente.genero == 'mulher':
                quadril = float(self.quadril_cm) if self.quadril_cm else cintura
                gordura_calc = 495 / (1.29579 - 0.35004 * math.log10(cintura + quadril - pescoco) + 0.22100 * math.log10(altura_cm)) - 450
            self.resultado_gordura = round(gordura_calc, 2)
        except:
            self.resultado_gordura = 0

        bf = self.resultado_gordura if self.resultado_gordura else 0
        if bf < 14 and self.cliente.genero == 'homem':
             self.classificacao = "Atleta / Fitness"
        elif bf < 21 and self.cliente.genero == 'mulher':
             self.classificacao = "Atleta / Fitness"
        elif self.resultado_imc > 25:
             self.classificacao = "Sobrepeso"
        else:
             self.classificacao = "Saudável"
        
        super(Avaliacao, self).save(*args, **kwargs)

# --- 3. PLANOS E TREINOS (Dependem de Cliente) ---
class PlanoAlimentar(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    data_criacao = models.DateTimeField(auto_now_add=True)
    observacoes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Plano Alimentar"
        verbose_name_plural = "Planos Alimentares"

    def __str__(self):
        return f"{self.titulo} - {self.cliente.nome}"

class Refeicao(models.Model):
    plano_alimentar = models.ForeignKey(PlanoAlimentar, on_delete=models.CASCADE)
    horario = models.TimeField()
    nome = models.CharField(max_length=100)
    descricao_alimentos = models.TextField()
    eh_suplementacao = models.BooleanField(default=False, verbose_name="É Suplementação?")

    class Meta:
        verbose_name = "Refeição"
        verbose_name_plural = "Refeições"

    def __str__(self):
        return f"{self.nome} ({self.horario})"

class PlanoTreino(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    LOCAL_CHOICES = [
        ('academia', 'Academia de Musculação'),
        ('casa', 'Em Casa'),
        ('crossfit', 'Box de CrossFit'),
        ('ao_ar_livre', 'Ao Ar Livre'),
    ]
    local = models.CharField(max_length=20, choices=LOCAL_CHOICES, default='academia')
    dias_semana = models.CharField(max_length=100, blank=True)
    observacoes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Plano de Treino"
        verbose_name_plural = "Planos de Treino"

    def __str__(self):
        return f"{self.titulo} - {self.cliente.nome}"

class Exercicio(models.Model):
    plano_treino = models.ForeignKey(PlanoTreino, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    series = models.IntegerField(default=3)
    repeticoes = models.CharField(max_length=50)
    carga_kg = models.CharField(max_length=50, blank=True, null=True)
    intervalo_segundos = models.IntegerField(default=60)
    video_demonstracao = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = "Exercício"
        verbose_name_plural = "Exercícios"

    def __str__(self):
        return self.nome

# --- 4. FICHAS E CONFIGURAÇÕES ---
class FichaAnamnese(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name='anamnese')
    data_preenchimento = models.DateTimeField(auto_now_add=True)
    # ... CAMPOS SOCIAIS ...
    ocupacao = models.CharField(max_length=100, null=True, blank=True)
    rotina_trabalho = models.CharField(max_length=20, choices=[('sedentario', 'Sedentário'), ('leve', 'Leve'), ('pesado', 'Pesado'), ('turnos', 'Turnos')], null=True, blank=True)
    composicao_familiar = models.CharField(max_length=200, null=True, blank=True)
    responsavel_compras = models.CharField(max_length=50, null=True, blank=True)
    # ... SAÚDE ...
    problema_cardiaco = models.BooleanField(default=False)
    dor_peito_atividade = models.BooleanField(default=False)
    dor_peito_repouso = models.BooleanField(default=False)
    tontura_perda_consciencia = models.BooleanField(default=False)
    problema_osseo = models.BooleanField(default=False)
    medicamento_pressao = models.BooleanField(default=False)
    historico_lesoes = models.TextField(blank=True)
    # ... SONO ...
    horas_sono = models.IntegerField(default=0)
    qualidade_sono = models.CharField(max_length=20, null=True, blank=True)
    ronca_apneia = models.BooleanField(default=False)
    higiene_sono_telas = models.BooleanField(default=False)
    # ... NUTRIÇÃO ...
    objetivo = models.CharField(max_length=50, null=True, blank=True)
    efeito_sanfona = models.BooleanField(default=False)
    dietas_previas = models.TextField(blank=True)
    consumo_agua = models.CharField(max_length=20, null=True, blank=True)
    intestino_preso = models.BooleanField(default=False)
    gases_estufamento = models.BooleanField(default=False)
    azia_refluxo = models.BooleanField(default=False)
    suplementos_farmacos = models.TextField(blank=True)
    # ... METABÓLICO ...
    fadiga_matinal = models.BooleanField(default=False)
    queda_energia_tarde = models.BooleanField(default=False)
    intolerancia_frio = models.BooleanField(default=False)
    queda_cabelo = models.BooleanField(default=False)
    desejo_sal_doce = models.BooleanField(default=False)
    # ... ESPECÍFICOS ...
    libido_baixa = models.BooleanField(default=False)
    forca_reduzida = models.BooleanField(default=False)
    ciclo_menstrual_regular = models.BooleanField(default=True)
    amenorreia = models.BooleanField(default=False)
    anticoncepcional = models.CharField(max_length=100, blank=True)
    # ... PSICO/TREINO ...
    motivacao_principal = models.CharField(max_length=50, null=True, blank=True)
    vergonha_corpo = models.CharField(max_length=20, null=True, blank=True)
    tempo_treino = models.CharField(max_length=20, null=True, blank=True)
    disponibilidade_treino = models.CharField(max_length=100, null=True, blank=True)
    exercicios_odiados = models.TextField(blank=True)
    observacoes_finais = models.TextField(blank=True)

    class Meta:
        verbose_name = "Ficha de Anamnese"
        verbose_name_plural = "Fichas de Anamnese"

    def __str__(self):
        return f"Anamnese de {self.cliente.nome}"

class ConfiguracaoAnamnese(models.Model):
    profissional = models.OneToOneField(User, on_delete=models.CASCADE)
    codigo_link = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    mostrar_social = models.BooleanField(default=True)
    mostrar_saude = models.BooleanField(default=True)
    mostrar_sono = models.BooleanField(default=True)
    mostrar_nutricao = models.BooleanField(default=True)
    mostrar_hormonios = models.BooleanField(default=True)
    mostrar_psico = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Configuração de Anamnese"
        verbose_name_plural = "Configurações de Anamnese"

    def __str__(self):
        return f"Configuração de {self.profissional.username}"

# --- 5. NOTIFICAÇÕES ---
class Notificacao(models.Model):
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    mensagem = models.TextField()
    lida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    link_acao = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        ordering = ['-data_criacao']

    def __str__(self):
        return f"{self.titulo} - {self.destinatario.username}"

# --- 6. CONSULTA / AGENDA (Depende de Cliente) ---
class Consulta(models.Model):
    profissional = models.ForeignKey(User, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    data_horario = models.DateTimeField(verbose_name="Data e Hora")
    status = models.CharField(max_length=20, choices=[('agendado', 'Agendado'), ('realizado', 'Realizado'), ('cancelado', 'Cancelado')], default='agendado')
    link_meet = models.URLField(blank=True, null=True, verbose_name="Link da Videochamada")
    observacoes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['data_horario']
        verbose_name = "Consulta"
        verbose_name_plural = "Agenda de Consultas"

    def __str__(self):
        return f"{self.cliente.nome} - {self.data_horario.strftime('%d/%m %H:%M')}"

# --- 7. ASSINATURA (PLANOS) ---
class Assinatura(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='assinatura')
    PLANOS_CHOICES = [
        ('gratuito', 'Teste Grátis (7 Dias - Ouro)'),
        ('bronze', 'Plano Bronze'),
        ('prata', 'Plano Prata'),
        ('ouro', 'Plano Ouro'),
    ]
    plano = models.CharField(max_length=20, choices=PLANOS_CHOICES, default='gratuito')
    data_inicio = models.DateTimeField(auto_now_add=True)
    data_validade = models.DateTimeField()
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.get_plano_display()}"

    @property
    def limite_clientes(self):
        if self.plano == 'bronze': return 500
        if self.plano == 'prata': return 1000
        return 999999

    @property
    def permite_fotos(self):
        return self.plano in ['ouro', 'gratuito']

    @property
    def permite_anamnese_personalizada(self):
        return self.plano != 'bronze'

    @property
    def dias_restantes(self):
        agora = timezone.now()
        if self.data_validade < agora: return 0
        delta = self.data_validade - agora
        return delta.days

# --- GATILHOS (SIGNALS) ---
@receiver(post_save, sender=User)
def criar_assinatura_teste(sender, instance, created, **kwargs):
    if created:
        Assinatura.objects.create(
            usuario=instance,
            plano='gratuito',
            data_validade=timezone.now() + timedelta(days=7)
        )

@receiver(post_save, sender=FichaAnamnese)
def criar_notificacao_anamnese(sender, instance, created, **kwargs):
    if created: 
        admins = User.objects.filter(is_superuser=True)
        for admin_user in admins:
            Notificacao.objects.create(
                destinatario=admin_user,
                titulo="📋 Nova Anamnese",
                mensagem=f"O cliente {instance.cliente.nome} enviou a ficha.",
                link_acao=f"/admin/core/cliente/{instance.cliente.id}/change/"
            )