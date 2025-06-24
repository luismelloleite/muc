import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from dotenv import load_dotenv

class Command(BaseCommand):
    """
    Comando Django para criar um superusuário de forma não interativa
    utilizando variáveis de ambiente.
    """
    help = (
        'Cria um superusuário para o projeto Django utilizando as '
        'variáveis de ambiente DJANGO_SUPERUSER_USERNAME, '
        'DJANGO_SUPERUSER_EMAIL e DJANGO_SUPERUSER_PASSWORD.'
    )

    def handle(self, *args, **options):
        load_dotenv()

        User = get_user_model()
        username = os.getenv('DJANGO_SUPERUSER_USERNAME')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

        if not all([username, email, password]):
            raise CommandError(
                "As variáveis de ambiente DJANGO_SUPERUSER_USERNAME, "
                "DJANGO_SUPERUSER_EMAIL e DJANGO_SUPERUSER_PASSWORD devem ser definidas."
            )

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"O superusuário '{username}' já existe."))
            return

        self.stdout.write(self.style.SUCCESS(f"Criando superusuário: {username}"))

        try:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS("Superusuário criado com sucesso."))
        except Exception as e:
            raise CommandError(f"Erro ao criar superusuário: {e}")