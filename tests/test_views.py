from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from visitantes.models import Visitante, CustomUser


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

    def test_visitante_create_view_admin(self):
        self.client.login(email='admin@example.com', password='adminpass123')
        response = self.client.get(reverse('visitantes:visitante_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'visitantes/visitante_form.html')

    def test_visitante_create_view_regular(self):
        self.client.login(email='user@example.com', password='userpass123')
        response = self.client.get(reverse('visitantes:visitante_create'))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_visitante_update_view_admin(self):
        self.client.login(email='admin@example.com', password='adminpass123')
        response = self.client.get(reverse('visitantes:visitante_update', args=[self.visitante.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'visitantes/visitante_form.html')

    def test_visitante_update_view_regular(self):
        self.client.login(email='user@example.com', password='userpass123')
        response = self.client.get(reverse('visitantes:visitante_update', args=[self.visitante.pk]))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_visitante_delete_view_admin(self):
        self.client.login(email='admin@example.com', password='adminpass123')
        response = self.client.get(reverse('visitantes:visitante_delete', args=[self.visitante.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'visitantes/visitante_confirm_delete.html')

    def test_visitante_delete_view_regular(self):
        self.client.login(email='user@example.com', password='userpass123')
        response = self.client.get(reverse('visitantes:visitante_delete', args=[self.visitante.pk]))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_relatorio_view_admin(self):
        self.client.login(email='admin@example.com', password='adminpass123')
        response = self.client.get(reverse('visitantes:relatorio'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'visitantes/relatorio.html')

    def test_relatorio_view_regular(self):
        self.client.login(email='user@example.com', password='userpass123')
        response = self.client.get(reverse('visitantes:relatorio'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'visitantes/relatorio.html')

    def test_user_list_view_admin(self):
        self.client.login(email='admin@example.com', password='adminpass123')
        response = self.client.get(reverse('visitantes:user_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'visitantes/user_list.html')

    def test_user_list_view_regular(self):
        self.client.login(email='user@example.com', password='userpass123')
        response = self.client.get(reverse('visitantes:user_list'))
        self.assertEqual(response.status_code, 403)  # Forbidden 