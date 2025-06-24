from rest_framework import viewsets
from .models import Visitante, CustomUser, LogAtividade
from .serializers import VisitanteSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime
import csv
import xlsxwriter
from io import BytesIO
from .forms import RelatorioForm, CustomUserCreationForm, CustomUserChangeForm, AdminUserUpdateForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView

class VisitanteViewSet(viewsets.ModelViewSet):
    queryset = Visitante.objects.all()
    serializer_class = VisitanteSerializer

def check_admin(user):
    return user.nivel_acesso == 'admin'

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.nivel_acesso == 'admin'
    
class EditRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.nivel_acesso in ['admin', 'edicao']

class UserListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = CustomUser
    template_name = 'visitantes/user_list.html'
    context_object_name = 'users'

class UserCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'visitantes/user_form.html'
    success_url = reverse_lazy('visitantes:user_list')

class UserUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = CustomUser
    form_class = AdminUserUpdateForm # Alterado para o novo formulário
    template_name = 'visitantes/user_form.html'
    success_url = reverse_lazy('visitantes:user_list')

    def form_valid(self, form):
        messages.success(self.request, f"Usuário '{form.instance.username}' atualizado com sucesso!")
        return super().form_valid(form)

class UserDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'visitantes/user_confirm_delete.html'
    success_url = reverse_lazy('visitantes:user_list')

class UserProfileView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'visitantes/user_profile.html'
    success_url = reverse_lazy('visitantes:user_profile')

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['password_form'] = PasswordChangeForm(self.request.user, self.request.POST)
        else:
            context['password_form'] = PasswordChangeForm(self.request.user)
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Perfil atualizado com sucesso!')
        return super().form_valid(form)

class PasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'visitantes/user_profile.html'
    success_url = reverse_lazy('visitantes:user_profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CustomUserChangeForm(instance=self.request.user)
        context['password_form'] = context.get('form_password', self.get_form())  # nome explícito
        return context


    def form_valid(self, form):
        messages.success(self.request, 'Senha alterada com sucesso!')
        return super().form_valid(form)


class VisitanteListView(LoginRequiredMixin, ListView):
    model = Visitante
    template_name = 'visitantes/visitante_list.html'
    context_object_name = 'visitantes'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        sort_by = self.request.GET.get('sort', '-horario_entrada')

        # Define os campos permitidos para ordenação
        allowed_sort_fields = {
            'nome': 'nome_completo',
            '-nome': '-nome_completo',
            'documento': 'numero_documento',
            '-documento': '-numero_documento',
            'visitado': 'visitado',
            '-visitado': '-visitado',
            'bloco': 'bloco',
            '-bloco': '-bloco',
            'entrada': 'horario_entrada',
            '-entrada': '-horario_entrada',
            'saida': 'horario_saida',
            '-saida': '-horario_saida',
        }

        # Aplica a ordenação
        sort_field = allowed_sort_fields.get(sort_by, '-horario_entrada')
        queryset = queryset.order_by(sort_field)

        # Aplica a busca
        if search_query:
            queryset = queryset.filter(
                Q(nome_completo__icontains=search_query) |
                Q(numero_documento__icontains=search_query) |
                Q(placa_veiculo__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_sort = self.request.GET.get('sort', '-entrada')
        search_query = self.request.GET.get('search', '')

        # Define as opções de ordenação
        context['sort_options'] = {
            'nome': 'Nome (A-Z)',
            '-nome': 'Nome (Z-A)',
            'documento': 'Documento (A-Z)',
            '-documento': 'Documento (Z-A)',
            'visitado': 'Visitado (A) (A-Z)',
            '-visitado': 'Visitado (A) (Z-A)',
            'bloco': 'Bloco (A-Z)',
            '-bloco': 'Bloco (Z-A)',
            'entrada': 'Entrada (Mais Antiga)',
            '-entrada': 'Entrada (Mais Recente)',
            'saida': 'Saída (Mais Antiga)',
            '-saida': 'Saída (Mais Recente)',
        }
        context['current_sort'] = current_sort
        context['search_query'] = search_query

        return context

class VisitanteCreateView(LoginRequiredMixin, EditRequiredMixin, CreateView):
    model = Visitante
    template_name = 'visitantes/visitante_form.html'
    fields = ['nome_completo', 'tipo_documento', 'numero_documento', 'visitado',
              'bloco', 'apartamento', 'placa_veiculo', 'marca_veiculo', 
              'modelo_veiculo', 'cor_veiculo']
    success_url = reverse_lazy('visitantes:visitante_list')

class VisitanteUpdateView(LoginRequiredMixin, EditRequiredMixin, UpdateView):
    model = Visitante
    template_name = 'visitantes/visitante_form.html'
    fields = ['nome_completo', 'tipo_documento', 'numero_documento', 'visitado',
              'bloco', 'apartamento', 'placa_veiculo', 'marca_veiculo', 
              'modelo_veiculo', 'cor_veiculo']
    success_url = reverse_lazy('visitantes:visitante_list')

    def form_valid(self, form):
        toggle_saida = self.request.POST.get('toggle_saida') == 'on'
        visitante = form.save(commit=False)

        # Lógica para alternar o status de saída
        if toggle_saida:
            if visitante.saida_registrada:
                visitante.horario_saida = None
            else:
                visitante.horario_saida = timezone.now()

        visitante.save()
        return super().form_valid(form)


class VisitanteDeleteView(LoginRequiredMixin, EditRequiredMixin, DeleteView):
    model = Visitante
    template_name = 'visitantes/visitante_confirm_delete.html'
    success_url = reverse_lazy('visitantes:visitante_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete(user=request.user)
        return redirect(success_url)

class RelatorioView(LoginRequiredMixin, FormView):
    template_name = 'visitantes/relatorio.html'
    form_class = RelatorioForm
    success_url = reverse_lazy('visitantes:relatorio')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Relatórios Personalizados'
        return context

    def form_valid(self, form):
        # Obter os dados do formulário
        campos = form.cleaned_data['campos']
        formato = form.cleaned_data['formato']
        
        # Construir a query com os filtros
        queryset = Visitante.objects.all()
        
        # Aplicar filtros
        if form.cleaned_data['data_inicio']:
            queryset = queryset.filter(horario_entrada__date__gte=form.cleaned_data['data_inicio'])
        if form.cleaned_data['data_fim']:
            queryset = queryset.filter(horario_entrada__date__lte=form.cleaned_data['data_fim'])
        if form.cleaned_data['bloco']:
            queryset = queryset.filter(bloco=form.cleaned_data['bloco'])
        if form.cleaned_data['tipo_documento']:
            queryset = queryset.filter(tipo_documento=form.cleaned_data['tipo_documento'])
        if form.cleaned_data['tem_veiculo'] == 'sim':
            queryset = queryset.exclude(placa_veiculo__isnull=True)
        elif form.cleaned_data['tem_veiculo'] == 'nao':
            queryset = queryset.filter(placa_veiculo__isnull=True)

        # Gerar o relatório no formato solicitado
        if formato == 'csv':
            return self.gerar_csv(queryset, campos)
        else:  # xlsx
            return self.gerar_excel(queryset, campos)

    def gerar_csv(self, queryset, campos):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="relatorio_visitantes_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        
        # Escrever cabeçalho
        writer.writerow([self.form_class.CAMPOS_CHOICES_DICT[campo] for campo in campos])
        
        # Escrever dados
        for visitante in queryset:
            row = []
            for campo in campos:
                valor = getattr(visitante, campo)
                if isinstance(valor, datetime):
                    valor = valor.strftime('%d/%m/%Y %H:%M')
                row.append(str(valor) if valor else '')
            writer.writerow(row)
        
        return response

    def gerar_excel(self, queryset, campos):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        # Formatação
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D9D9D9',
            'border': 1
        })
        cell_format = workbook.add_format({
            'border': 1
        })

        # Escrever cabeçalho
        for col, campo in enumerate(campos):
            worksheet.write(0, col, self.form_class.CAMPOS_CHOICES_DICT[campo], header_format)
            worksheet.set_column(col, col, 20)  # Ajustar largura da coluna

        # Escrever dados
        for row, visitante in enumerate(queryset, start=1):
            for col, campo in enumerate(campos):
                valor = getattr(visitante, campo)
                if isinstance(valor, datetime):
                    valor = valor.strftime('%d/%m/%Y %H:%M')
                worksheet.write(row, col, str(valor) if valor else '', cell_format)

        workbook.close()
        output.seek(0)

        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="relatorio_visitantes_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
        return response

class AuditoriaListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = LogAtividade
    template_name = 'visitantes/auditoria_list.html'
    context_object_name = 'logs'
    paginate_by = 10  # Paginação com 10 itens por página

    def test_func(self):
        # Apenas administradores podem acessar a página de auditoria
        return self.request.user.nivel_acesso == 'admin'

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        order_by = self.request.GET.get('order_by', '-data_hora')  # Ordenação padrão: mais recente

        # Filtrar logs com base na busca
        if search_query:
            queryset = queryset.filter(
                modelo__icontains=search_query
            )

        # Ordenar os logs
        return queryset.order_by(order_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['order_by'] = self.request.GET.get('order_by', '-data_hora')
        return context
