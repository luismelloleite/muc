from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import CustomUser, Visitante
from .forms import CustomUserCreationForm, CustomUserChangeForm, RelatorioForm
from django.core.exceptions import ValidationError

class CustomUserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123',
            'nivel_acesso': 'admin'
        }

    def test_create_user(self):
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.nivel_acesso, self.user_data['nivel_acesso'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        user = CustomUser.objects.create_superuser(**self.user_data)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.nivel_acesso, 'admin')

    def test_user_str_representation(self):
        user = CustomUser.objects.create_user(**self.user_data)
        expected_str = f"{user.get_full_name()} ({user.get_nivel_acesso_display()})"
        self.assertEqual(str(user), expected_str)

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create admin user
        self.admin_user = CustomUser.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='adminpass123',
            nivel_acesso='admin'
        )
        
        # Create regular user
        self.regular_user = CustomUser.objects.create_user(
            email='user@example.com',
            username='user',
            password='userpass123',
            nivel_acesso='visualizacao'
        )
        
        # Create a visitante
        self.visitante = Visitante.objects.create(
            nome_completo='Test Visitante',
            tipo_documento='RG',
            numero_documento='123456789',
            bloco='A',
            apartamento='101'
        )

    def test_visitante_list_view_admin(self):
        self.client.login(email='admin@example.com', password='adminpass123')
        response = self.client.get(reverse('visitantes:visitante_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'visitantes/visitante_list.html')

    def test_visitante_list_view_regular(self):
        self.client.login(email='user@example.com', password='userpass123')
        response = self.client.get(reverse('visitantes:visitante_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'visitantes/visitante_list.html')

class FormTests(TestCase):
    def setUp(self):
        self.valid_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'nivel_acesso': 'admin'
        }

        self.valid_report_data = {
            'campos': ['nome_completo', 'tipo_documento'],
            'formato': 'csv',
            'data_inicio': '2024-01-01',
            'data_fim': '2024-12-31',
            'bloco': 'A',
            'tipo_documento': 'RG',
            'tem_veiculo': 'sim'
        }

    def test_valid_form(self):
        form = CustomUserCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        data = self.valid_data.copy()
        data['email'] = 'invalid-email'
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_valid_report_form(self):
        form = RelatorioForm(data=self.valid_report_data)
        self.assertTrue(form.is_valid())

    def test_invalid_report_dates(self):
        data = self.valid_report_data.copy()
        data['data_inicio'] = '2024-12-31'
        data['data_fim'] = '2024-01-01'
        form = RelatorioForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertEqual(form.errors['__all__'][0], 'A data final não pode ser anterior à data inicial.')
        self.assertEqual(len(form.errors), 1)
