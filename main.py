#!/usr/bin/env python
"""
Entry point para o executável do Sistema de Controle de Visitantes
Substitui o run_server.bat com funcionalidade equivalente
"""

import os
import sys
import time
import webbrowser
import subprocess
from pathlib import Path

def get_app_directory():
    """
    Retorna o diretório da aplicação.
    Se executado como .exe, usa o diretório temporário do PyInstaller.
    """
    if getattr(sys, 'frozen', False):
        # Executando como .exe
        return Path(sys._MEIPASS)
    else:
        # Executando como script Python
        return Path(__file__).parent

def check_server_running(host='127.0.0.1', port=8000):
    """Verifica se o servidor já está rodando na porta especificada"""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def run_django_setup():
    """Executa a configuração inicial do Django (migrações, superuser, etc.)"""
    app_dir = get_app_directory()
    
    print("Configurando aplicação...")
    
    # Mudar para o diretório da aplicação
    original_dir = os.getcwd()
    os.chdir(app_dir)
    
    # Definir variável de ambiente para o Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portaria_muc.settings')
    
    try:
        # Carregar variáveis do .env
        from dotenv import load_dotenv
        load_dotenv()
        
        # Importar Django para usar management commands programaticamente
        import django
        from django.core.management import execute_from_command_line
        from django.conf import settings
        
        # Configurar Django
        django.setup()
        
        # Executar migrações
        print("Aplicando migrações...")
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=0'])
        
        # Criar superuser (ler credenciais do .env)
        print("Configurando usuário administrador...")
        
        # Ler credenciais do .env
        superuser_username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
        superuser_email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@muc.ufcat.edu.br')
        superuser_password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123')
        
        # Definir variáveis de ambiente para o comando
        os.environ['DJANGO_SUPERUSER_USERNAME'] = superuser_username
        os.environ['DJANGO_SUPERUSER_EMAIL'] = superuser_email
        os.environ['DJANGO_SUPERUSER_PASSWORD'] = superuser_password
        
        try:
            execute_from_command_line(['manage.py', 'create_superuser'])
            print(f"   👤 Usuário criado: {superuser_username}")
        except SystemExit:
            # create_superuser pode dar SystemExit, mas é normal
            print(f"   👤 Usuário configurado: {superuser_username}")
        except Exception as e:
            print(f"      ⚠️  Aviso: {e}")
        
        print("✅ Configuração concluída!")
        return True
        
    except Exception as e:
        print(f"Erro na configuração: {e}")
        return False
    finally:
        # Voltar ao diretório original
        os.chdir(original_dir)

def start_server():
    """Inicia o servidor Django usando runserver --noreload"""
    app_dir = get_app_directory()
    
    print("Iniciando servidor...")
    
    # Mudar para o diretório da aplicação
    original_dir = os.getcwd()
    os.chdir(app_dir)
    
    # Definir variável de ambiente para o Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portaria_muc.settings')
    
    try:
        # Importar Django para usar management commands
        import django
        from django.core.management import execute_from_command_line
        
        # Configurar Django
        django.setup()
        
        print("Iniciando servidor Django...")
        
        # Executar runserver com --noreload
        execute_from_command_line([
            "manage.py", 
            "runserver", 
            "127.0.0.1:8000",
            "--noreload"
        ])
        
        print("✅ Servidor iniciado com sucesso!")
        return True
        
    except KeyboardInterrupt:
        print("Servidor interrompido pelo usuário")
        return True
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")
        return False
    finally:
        # Voltar ao diretório original
        os.chdir(original_dir)

def open_browser():
    """Abre o navegador na aplicação"""
    url = 'http://127.0.0.1:8000'
    print(f"Abrindo navegador em {url}...")
    
    try:
        webbrowser.open(url)
        return True
    except Exception as e:
        print(f"Não foi possível abrir o navegador automaticamente: {e}")
        print(f"Acesse manualmente: {url}")
        return False

def check_first_run():
    """Verifica se é a primeira execução do sistema"""
    app_dir = get_app_directory()
    
    # Se executando como .exe, verificar na pasta onde está o executável
    if getattr(sys, 'frozen', False):
        # Executável: verificar na pasta do executável
        exe_dir = Path(sys.executable).parent
        flag_file = exe_dir / '.portaria_configured'
    else:
        # Desenvolvimento: verificar na pasta da aplicação
        flag_file = app_dir / '.portaria_configured'
    
    return not flag_file.exists()

def mark_as_configured():
    """Marca o sistema como configurado"""
    app_dir = get_app_directory()
    
    # Se executando como .exe, criar flag na pasta onde está o executável
    if getattr(sys, 'frozen', False):
        exe_dir = Path(sys.executable).parent
        flag_file = exe_dir / '.portaria_configured'
    else:
        flag_file = app_dir / '.portaria_configured'
    
    try:
        flag_file.write_text(f"Configurado em: {time.strftime('%d/%m/%Y %H:%M:%S')}")
        return True
    except Exception as e:
        print(f"Aviso: Não foi possível criar arquivo de configuração: {e}")
        return False

def main():
    """Função principal"""
    # Verificar se foi passado parâmetro schedule_sync
    if len(sys.argv) > 1 and sys.argv[1] == 'schedule_sync':
        run_schedule_sync()
        return
    
    print("=" * 60)
    print("  Sistema de Controle de Visitantes - MUC/UFCAT")
    print("=" * 60)
    
    # Verificar se servidor já está rodando
    if check_server_running():
        print("Servidor já está rodando!")
        print("Abrindo navegador...")
        open_browser()
        return
    
    # Verificar se é primeira execução
    is_first_run = check_first_run()
    
    # Configurar aplicação (primeira execução ou se necessário)
    if not run_django_setup():
        input("Falha na configuração. Pressione Enter para sair...")
        return
    
    # Se é primeira execução, configurar sincronização automática
    if is_first_run:
        print("\nConfigurando sincronização automática (primeira execução)...")
        if run_schedule_sync():
            mark_as_configured()
            print("Sistema totalmente configurado!")
        else:
            print("Sistema funcionando, mas sincronização automática não foi configurada")
    
    print("\n" + "=" * 60)
    print("Sistema pronto para uso!")
    print("Acesso: http://127.0.0.1:8000")
    print("Para parar: Ctrl+C")
    print("=" * 60)
    
    # Aguardar um pouco antes de abrir o navegador
    print("\nAbrindo navegador em 3 segundos...")
    time.sleep(3)
    open_browser()
    
    # Iniciar servidor (isso vai bloquear até o usuário parar)
    start_server()
    
    print("\nSistema encerrado!")

def run_schedule_sync():
    """Executa o comando schedule_sync do Django"""
    app_dir = get_app_directory()
    
    print("Configurando sincronização automática...")
    
    # Mudar para o diretório da aplicação
    original_dir = os.getcwd()
    os.chdir(app_dir)
    
    # Definir variável de ambiente para o Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portaria_muc.settings')
    
    try:
        # Carregar variáveis do .env
        from dotenv import load_dotenv
        load_dotenv()
        
        # Importar Django para usar management commands
        import django
        from django.core.management import execute_from_command_line
        
        # Configurar Django
        django.setup()
        
        # Executar schedule_sync
        print("   ⏰ Criando agendamento de sincronização...")
        execute_from_command_line(['manage.py', 'schedule_sync'])
        
        print("✅ Sincronização automática configurada!")
        print("   📅 Executará diariamente à meia-noite")
        return True
        
    except Exception as e:
        print(f"Erro ao configurar sincronização: {e}")
        return False
    finally:
        # Voltar ao diretório original
        os.chdir(original_dir)

if __name__ == "__main__":
    main()