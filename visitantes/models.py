from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('O email é obrigatório'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('nivel_acesso', 'admin')
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    NIVEL_ACESSO_CHOICES = [
        ('admin', 'Administração'),
        ('edicao', 'Edição'),
        ('visualizacao', 'Visualização'),
    ]

    email = models.EmailField(_('email address'), unique=True)
    nivel_acesso = models.CharField(
        max_length=20,
        choices=NIVEL_ACESSO_CHOICES,
        default='visualizacao',
        verbose_name='Nível de Acesso'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    # Add related_name to avoid clashes with auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='customuser_set',
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='customuser_set',
        related_query_name='customuser',
    )

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_nivel_acesso_display()})"

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'


class VisitanteManager(models.Manager):
    def get_queryset(self):
        # Por padrão, retorna apenas visitantes não excluídos
        return super().get_queryset().filter(data_exclusao__isnull=True)


class Visitante(models.Model):
    nome_completo = models.CharField(max_length=255)
    tipo_documento = models.CharField(max_length=50)
    numero_documento = models.CharField(max_length=100)    
    visitado = models.CharField(max_length=255)

    placa_veiculo = models.CharField(max_length=10, blank=True, null=True)
    marca_veiculo = models.CharField(max_length=50, blank=True, null=True)
    modelo_veiculo = models.CharField(max_length=50, blank=True, null=True)
    cor_veiculo = models.CharField(max_length=30, blank=True, null=True)

    bloco = models.CharField(max_length=10)
    apartamento = models.CharField(max_length=10)
    horario_entrada = models.DateTimeField(default=timezone.now)
    horario_saida = models.DateTimeField(null=True, blank=True)

    sincronizado = models.BooleanField(default=True)  # para controle offline

    # Campos de auditoria
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    data_exclusao = models.DateTimeField(blank=True, null=True)
    usuario_ultima_acao = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='visitantes_modificados',
        verbose_name='Usuário Última Ação'
    )

    objects = VisitanteManager()  # Manager padrão (apenas ativos)
    all_objects = models.Manager() # Manager para todos os objetos (incluindo excluídos)

    @property
    def saida_registrada(self):
        """Propriedade que retorna True se há horário de saída"""
        return self.horario_saida is not None
    
    def toggle_saida(self):
        """Alterna entre marcar/desmarcar a saída"""
        if self.horario_saida:
            self.horario_saida = None  # Desmarca
        else:
            self.horario_saida = timezone.now()  # Marca com hora atual
        self.save()

    def delete(self, using=None, keep_parents=False, user=None):
        self.data_exclusao = timezone.now()
        update_fields = ['data_exclusao']

        if user and hasattr(user, 'is_authenticated') and user.is_authenticated:
            self.usuario_ultima_acao = user
            update_fields.append('usuario_ultima_acao')

        self.save(using=using, update_fields=update_fields)

    def undelete(self, using=None, user=None):
        """Restaura um visitante que sofreu soft delete."""
        self.data_exclusao = None
        update_fields = ['data_exclusao'] # data_atualizacao será atualizada automaticamente

        if user and hasattr(user, 'is_authenticated') and user.is_authenticated:
            self.usuario_ultima_acao = user
            update_fields.append('usuario_ultima_acao')
        self.save(using=using, update_fields=update_fields)

    def __str__(self):
        return self.nome_completo


class LogAtividade(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Usuário'
    )
    acao = models.CharField(max_length=50, verbose_name='Ação')
    modelo = models.CharField(max_length=100, verbose_name='Modelo')
    objeto_id = models.PositiveIntegerField(verbose_name='ID do Objeto')
    descricao = models.TextField(verbose_name='Descrição', blank=True)  # Pode armazenar o payload
    data_hora = models.DateTimeField(auto_now_add=True, verbose_name='Data e Hora')

    def __str__(self):
        return f"{self.usuario} - {self.acao} - {self.modelo} - {self.objeto_id}"

    class Meta:
        verbose_name = 'Log de Atividade'
        verbose_name_plural = 'Logs de Atividades'
        ordering = ['-data_hora']
