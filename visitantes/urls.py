from django.urls import path
from . import views
from .views import AuditoriaListView

app_name = 'visitantes'

urlpatterns = [
    # User management URLs
    path('usuarios/', views.UserListView.as_view(), name='user_list'),
    path('usuarios/novo/', views.UserCreateView.as_view(), name='user_create'),
    path('usuarios/<int:pk>/editar/', views.UserUpdateView.as_view(), name='user_update'),
    path('usuarios/<int:pk>/excluir/', views.UserDeleteView.as_view(), name='user_delete'),

    # Visitor management URLs
    path('', views.VisitanteListView.as_view(), name='visitante_list'),
    path('novo/', views.VisitanteCreateView.as_view(), name='visitante_create'),
    path('<int:pk>/editar/', views.VisitanteUpdateView.as_view(), name='visitante_update'),
    path('<int:pk>/excluir/', views.VisitanteDeleteView.as_view(), name='visitante_delete'),
    
    # Report URLs
    path('relatorio/', views.RelatorioView.as_view(), name='relatorio'),
    path('perfil/', views.UserProfileView.as_view(), name='user_profile'),
    path('perfil/alterar-senha/', views.PasswordChangeView.as_view(), name='change_password'),
    path('auditoria/', AuditoriaListView.as_view(), name='auditoria_list'),
]
