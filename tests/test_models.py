from django.test import TestCase
from django.utils import timezone
from visitantes.models import CustomUser, Visitante

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

class VisitanteModelTest(TestCase):
    def setUp(self):
        self.visitante_data = {
            'nome_completo': 'João Silva',
            'tipo_documento': 'RG',
            'numero_documento': '123456789',
            'bloco': 'A',
            'apartamento': '101',
            'placa_veiculo': 'ABC1234',
            'marca_veiculo': 'Toyota',
            'modelo_veiculo': 'Corolla',
            'cor_veiculo': 'Prata'
        }

    def test_create_visitante(self):
        visitante = Visitante.objects.create(**self.visitante_data)
        self.assertEqual(visitante.nome_completo, self.visitante_data['nome_completo'])
        self.assertEqual(visitante.tipo_documento, self.visitante_data['tipo_documento'])
        self.assertEqual(visitante.numero_documento, self.visitante_data['numero_documento'])
        self.assertEqual(visitante.bloco, self.visitante_data['bloco'])
        self.assertEqual(visitante.apartamento, self.visitante_data['apartamento'])
        self.assertEqual(visitante.placa_veiculo, self.visitante_data['placa_veiculo'])
        self.assertEqual(visitante.marca_veiculo, self.visitante_data['marca_veiculo'])
        self.assertEqual(visitante.modelo_veiculo, self.visitante_data['modelo_veiculo'])
        self.assertEqual(visitante.cor_veiculo, self.visitante_data['cor_veiculo'])
        self.assertTrue(visitante.sincronizado)
        self.assertIsNotNone(visitante.horario_entrada)

    def test_visitante_str_representation(self):
        visitante = Visitante.objects.create(**self.visitante_data)
        self.assertEqual(str(visitante), self.visitante_data['nome_completo'])

    def test_visitante_optional_fields(self):
        # Test creating visitante without vehicle information
        data_without_vehicle = {
            'nome_completo': 'Maria Silva',
            'tipo_documento': 'CPF',
            'numero_documento': '987654321',
            'bloco': 'B',
            'apartamento': '202'
        }
        visitante = Visitante.objects.create(**data_without_vehicle)
        self.assertIsNone(visitante.placa_veiculo)
        self.assertIsNone(visitante.marca_veiculo)
        self.assertIsNone(visitante.modelo_veiculo)
        self.assertIsNone(visitante.cor_veiculo) 