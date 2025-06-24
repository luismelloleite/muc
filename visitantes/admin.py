from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Visitante

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'nivel_acesso', 'is_active', 'is_staff')
    list_filter = ('nivel_acesso', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informações Pessoais'), {'fields': ('first_name', 'last_name', 'username')}),
        (_('Permissões'), {
            'fields': ('nivel_acesso', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Datas Importantes'), {'fields': ('last_login', 'date_joined', 'data_criacao', 'data_atualizacao')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'username', 'nivel_acesso'),
        }),
    )

@admin.action(description='Restaurar visitantes selecionados')
def restaurar_visitantes(modeladmin, request, queryset):
    """
    Ação para restaurar visitantes que sofreram soft delete.
    """
    for visitante in queryset:
        visitante.undelete(user=request.user)
    modeladmin.message_user(request, f"{queryset.count()} visitante(s) restaurado(s) com sucesso.")

@admin.register(Visitante)
class VisitanteAdmin(admin.ModelAdmin):
    list_display = (
        'nome_completo', 'tipo_documento', 'numero_documento', 'visitado',
        'bloco', 'apartamento', 'horario_entrada', 'horario_saida',
        'data_exclusao', 'usuario_ultima_acao'
    )
    list_filter = ('tipo_documento', 'bloco', 'horario_entrada', 'data_exclusao')
    search_fields = ('nome_completo', 'numero_documento', 'bloco', 'apartamento', 'placa_veiculo')
    date_hierarchy = 'horario_entrada'
    ordering = ('-horario_entrada',)
    actions = [restaurar_visitantes]

    def get_queryset(self, request):
        # Usa o manager que retorna todos os objetos, incluindo os deletados
        return Visitante.all_objects.get_queryset()

    fieldsets = (
        (None, {
            'fields': ('nome_completo', 'tipo_documento', 'numero_documento', 'visitado')
        }),
        ('Localização', {
            'fields': ('bloco', 'apartamento')
        }),
        ('Veículo', {
            'fields': ('placa_veiculo', 'marca_veiculo', 'modelo_veiculo', 'cor_veiculo'),
            'classes': ('collapse',)
        }),
        ('Informações Adicionais', {
            'fields': ('horario_entrada', 'horario_saida', 'sincronizado'),
            'classes': ('collapse',)
        }),
    )