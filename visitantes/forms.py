from sqlite3 import OperationalError
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from .models import Visitante, CustomUser
from django.core.exceptions import ValidationError
from datetime import datetime

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'nivel_acesso')
        labels = {
            'email': 'Email',
            'username': 'Nome de usuário',
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'nivel_acesso': 'Nível de Acesso'
        }

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name') # username não é editável pelo próprio usuário aqui
        labels = {
            'email': 'Email',
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # O UserChangeForm original já lida com o campo 'password' de forma especial (não como um input direto)
        # e torna 'username' readonly se o usuário não for superuser.
        # Aqui, como 'username' não está nos fields, não precisamos nos preocupar com readonly.
        if 'password' in self.fields:
            del self.fields['password']

class AdminUserUpdateForm(forms.ModelForm):
    new_password1 = forms.CharField(
        label='Nova Senha',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        required=False,
        help_text="Deixe em branco para não alterar a senha."
    )
    new_password2 = forms.CharField(
        label='Confirmar Nova Senha',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'nivel_acesso', 'is_active')
        labels = {
            'email': 'Email',
            'username': 'Nome de usuário',
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'nivel_acesso': 'Nível de Acesso',
            'is_active': 'Ativo'
        }

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get("new_password1")
        new_password2 = self.cleaned_data.get("new_password2")
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("As senhas não coincidem.", code='password_mismatch')
        return new_password2

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password1 = self.cleaned_data.get("new_password1")
        if new_password1:
            user.set_password(new_password1)
        if commit:
            user.save()
        return user

class RelatorioForm(forms.Form):
    # Opções de campos para seleção
    CAMPOS_CHOICES = [
        ('nome_completo', 'Nome Completo'),
        ('tipo_documento', 'Tipo de Documento'),
        ('numero_documento', 'Número do Documento'),
        ('visitado', 'Visitado (A)'),
        ('bloco', 'Bloco'),
        ('apartamento', 'Apartamento'),
        ('horario_entrada', 'Horário de Entrada'),
        ('horario_saida', 'Horário de Saida'),
        ('placa_veiculo', 'Placa do Veículo'),
        ('marca_veiculo', 'Marca do Veículo'),
        ('modelo_veiculo', 'Modelo do Veículo'),
        ('cor_veiculo', 'Cor do Veículo'),
    ]

    # Dicionário para mapear os campos aos seus labels
    CAMPOS_CHOICES_DICT = dict(CAMPOS_CHOICES)

    # Opções de formato de exportação
    FORMATO_CHOICES = [
        ('csv', 'CSV'),
        ('xlsx', 'Excel'),
    ]

    # Campos selecionados para o relatório
    campos = forms.MultipleChoiceField(
        choices=CAMPOS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='Campos do Relatório'
    )

    # Formato de exportação
    formato = forms.ChoiceField(
        choices=FORMATO_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label='Formato de Exportação'
    )

    # Filtros
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Data Inicial'
    )
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Data Final'
    )
    bloco = forms.ChoiceField(
        choices=[('', 'Todos')],
        required=False,
        label='Bloco'
    )
    tipo_documento = forms.ChoiceField(
        choices=[('', 'Todos')],
        required=False,
        label='Tipo de Documento'
    )
    tem_veiculo = forms.ChoiceField(
        choices=[('', 'Todos'), ('sim', 'Com Veículo'), ('nao', 'Sem Veículo')],
        required=False,
        label='Veículo'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            from .models import Visitante
            distinct_blocos = Visitante.objects.values_list('bloco', flat=True).distinct().order_by('bloco')
            self.fields['bloco'].choices = [('', 'Todos')] + [(b, b) for b in distinct_blocos if b]

            distinct_tipos_documento = Visitante.objects.values_list('tipo_documento', flat=True).distinct().order_by('tipo_documento')
            self.fields['tipo_documento'].choices = [('', 'Todos')] + [(t, t) for t in distinct_tipos_documento if t]

        except (OperationalError, ImportError) as e:
            print(f"Aviso: Não foi possível popular dinamicamente as choices para RelatorioForm: {e}")
            pass

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')

        if data_inicio and data_fim and data_fim < data_inicio:
            raise ValidationError('A data final não pode ser anterior à data inicial.')

        return cleaned_data 