from django.core.management.base import BaseCommand
import os
import sys
from django.conf import settings

class Command(BaseCommand):
    help = 'Cria um agendamento no Windows para executar a sincronização de visitantes'

    def handle(self, *args, **options):
        try:
            # Caminho para o script de sincronização
            project_path = settings.BASE_DIR
            python_path = sys.executable
            manage_path = os.path.join(project_path, 'manage.py')
            sync_command = f'"{python_path}" "{manage_path}" sync_visitantes'

            # Cria o arquivo batch para executar a sincronização
            batch_path = os.path.join(project_path, 'sync_visitantes.bat')
            with open(batch_path, 'w') as f:
                f.write(f'@echo off\n')
                f.write(f'cd /d "{project_path}"\n')
                f.write(f'{sync_command}\n')
                f.write(f'exit\n')

            # Cria o comando para agendar a tarefa
            task_name = "Sincronização de Visitantes"
            task_command = (
                f'schtasks /create /tn "{task_name}" /tr "{batch_path}" '
                f'/sc daily /st 00:00 /ru SYSTEM /f'
            )

            # Executa o comando para criar a tarefa agendada
            os.system(task_command)

            self.stdout.write(self.style.SUCCESS('Tarefa agendada criada com sucesso!'))
            self.stdout.write(self.style.SUCCESS(f'Script batch criado em: {batch_path}'))
            self.stdout.write(self.style.SUCCESS('A sincronização será executada diariamente à meia-noite.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao criar o agendamento: {str(e)}')) 