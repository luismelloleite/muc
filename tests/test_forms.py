from django.test import TestCase
from visitantes.forms import CustomUserCreationForm, CustomUserChangeForm, RelatorioForm
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class CustomUserCreationFormTest(TestCase):
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

    def test_valid_form(self):
        form = CustomUserCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        data = self.valid_data.copy()
        data['email'] = 'invalid-email'
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_password_mismatch(self):
        data = self.valid_data.copy()
        data['password2'] = 'differentpass'
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_missing_required_fields(self):
        data = self.valid_data.copy()
        del data['email']
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

class CustomUserChangeFormTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            nivel_acesso='admin'
        )
        self.valid_data = {
            'email': 'new@example.com',
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'nivel_acesso': 'visualizacao',
            'is_active': True
        }

    def test_valid_form(self):
        form = CustomUserChangeForm(data=self.valid_data, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        data = self.valid_data.copy()
        data['email'] = 'invalid-email'
        form = CustomUserChangeForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

class RelatorioFormTest(TestCase):
    def setUp(self):
        self.valid_data = {
            'campos': ['nome_completo', 'tipo_documento', 'numero_documento'],
            'formato': 'csv',
            'data_inicio': '2024-01-01',
            'data_fim': '2024-12-31',
            'bloco': 'A',
            'tipo_documento': 'RG',
            'tem_veiculo': 'sim'
        }

    def test_valid_form(self):
        form = RelatorioForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_invalid_date_range(self):
        data = self.valid_data.copy()
        data['data_inicio'] = '2024-12-31'
        data['data_fim'] = '2024-01-01'
        form = RelatorioForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertEqual(form.errors['__all__'][0], 'A data final não pode ser anterior à data inicial.')
        self.assertEqual(len(form.errors), 1)  # Verifica se há apenas um erro

    def test_missing_required_fields(self):
        data = self.valid_data.copy()
        del data['campos']
        form = RelatorioForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('campos', form.errors)

    def test_invalid_format(self):
        data = self.valid_data.copy()
        data['formato'] = 'invalid'
        form = RelatorioForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('formato', form.errors) 