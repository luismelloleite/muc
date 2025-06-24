import subprocess
import os
import sys

VENV_NAME = "venv"

def run_command(command, check=True, env=None):
    """
    Executa um comando do sistema de forma robusta, lidando com possíveis
    erros de codificação na saída.
    """
    cmd_str = ' '.join(command) if isinstance(command, list) else command
    print(f"\n▶️ Executando: {cmd_str}")
    try:
        # 1. Captura a saída como bytes brutos, removendo 'text=True' e 'encoding'.
        process = subprocess.run(
            command,
            capture_output=True,
            check=check,
            env=env
        )

        # 2. Decodifica a saída de forma segura.
        stdout_str = ""
        stderr_str = ""
        if process.stdout:
            try:
                # Tenta decodificar como UTF-8 primeiro.
                stdout_str = process.stdout.decode('utf-8')
            except UnicodeDecodeError:
                # Se falhar, usa uma codificação de fallback comum do Windows
                # e substitui quaisquer caracteres problemáticos.
                print("   ⚠️  Aviso: a saída não é UTF-8. Usando fallback de decodificação.")
                stdout_str = process.stdout.decode('cp1252', errors='replace')
        
        if process.stderr:
            try:
                stderr_str = process.stderr.decode('utf-8')
            except UnicodeDecodeError:
                stderr_str = process.stderr.decode('cp1252', errors='replace')

        # Imprime a saída decodificada.
        if stdout_str:
            print("   Saída:")
            print("   " + "   ".join(stdout_str.strip().splitlines(True)))
        if stderr_str:
            print("   Erros (stderr):")
            print("   " + "   ".join(stderr_str.strip().splitlines(True)))
            
        print(f"✅ Comando '{cmd_str}' executado com sucesso.")
        return True

    except subprocess.CalledProcessError as e:
        # A lógica de erro para comandos que retornam um código de falha.
        # Também decodifica a saída de forma segura.
        print(f"❌ Erro ao executar o comando: {cmd_str} (código de saída: {e.returncode})")
        stdout_err = e.stdout.decode('utf-8', errors='replace') if e.stdout else ""
        stderr_err = e.stderr.decode('utf-8', errors='replace') if e.stderr else ""
        if stdout_err:
            print("   Saída do erro:\n   " + "   ".join(stdout_err.strip().splitlines(True)))
        if stderr_err:
            print("   Stderr do erro:\n   " + "   ".join(stderr_err.strip().splitlines(True)))
        return False
    except FileNotFoundError:
        cmd_name = command[0] if isinstance(command, list) else command.split()[0]
        print(f"❌ Erro: Comando ou executável não encontrado: {cmd_name}")
        return False
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado: {e}")
        return False

def get_venv_paths(project_root):
    """Retorna os caminhos para os executáveis do venv de acordo com o SO."""
    if sys.platform == "win32":
        python_path = os.path.join(project_root, VENV_NAME, "Scripts", "python.exe")
    else: # Linux, macOS, etc.
        python_path = os.path.join(project_root, VENV_NAME, "bin", "python")
    return python_path

def main():
    """Função principal para configurar o projeto Django."""
    project_root = os.getcwd()
    print(f"Iniciando configuração do projeto Django em: {project_root}")

    # --- ALTERAÇÃO 1: Criar o ambiente modificado ---
    # Cria uma cópia do ambiente atual do sistema.
    env_utf8 = os.environ.copy()
    # Adiciona a variável que força o Python a usar UTF-8 para I/O.
    env_utf8['PYTHONUTF8'] = '1'
    print("ℹ️  Ambiente configurado para passar PYTHONUTF8=1 para todos os subprocessos.")
    # ----------------------------------------------

    # 1. Criar ambiente virtual (venv)
    print("\n--- Etapa 1: Criando ambiente virtual ---")
    if os.path.isdir(os.path.join(project_root, VENV_NAME)):
        print(f"ℹ️  A pasta '{VENV_NAME}' já existe. Pulando a criação do venv.")
    else:
        # --- ALTERAÇÃO 2: Passar o ambiente para a chamada ---
        if not run_command([sys.executable, "-m", "venv", VENV_NAME], env=env_utf8):
            print("❌ Falha ao criar o ambiente virtual. Abortando.")
            return

    # Pega os caminhos corretos para o SO atual
    python_executable_in_venv = get_venv_paths(project_root)

    # Verificar se o executável do venv foi criado
    if not os.path.exists(python_executable_in_venv):
        print(f"❌ Erro crítico: Executável Python do venv não encontrado em '{python_executable_in_venv}'.")
        return

    # 2. Ativação e instruções
    print("\n--- Ativação do Ambiente Virtual ---")
    print(f"ℹ️  Os próximos comandos usarão o interpretador: '{python_executable_in_venv}'.")
    activate_command = f".\\{VENV_NAME}\\Scripts\\activate" if sys.platform == "win32" else f"source {VENV_NAME}/bin/activate"
    print(f"   Para ativar manualmente no seu terminal, execute: {activate_command}")

    # 3. Instalar requirements.txt
    print("\n--- Etapa 3: Instalando dependências ---")
    requirements_file = os.path.join(project_root, "requirements.txt")
    if not os.path.exists(requirements_file):
        print("⚠️  Arquivo 'requirements.txt' não encontrado. Pulando a instalação de dependências.")
    else:
        # --- ALTERAÇÃO 2: Passar o ambiente para a chamada ---
        if not run_command([python_executable_in_venv, "-m", "pip", "install", "-r", requirements_file], env=env_utf8):
            print("❌ Falha ao instalar as dependências. Verifique o arquivo 'requirements.txt'.")

    # Verificar se manage.py existe
    manage_py_path = os.path.join(project_root, "manage.py")
    if not os.path.exists(manage_py_path):
        print(f"❌ Erro: 'manage.py' não encontrado em {project_root}.")
        return

    # 4. python manage.py makemigrations
    print("\n--- Etapa 4: Criando migrações (makemigrations) ---")
    # --- ALTERAÇÃO 2: Passar o ambiente para a chamada ---
    if not run_command([python_executable_in_venv, manage_py_path, "makemigrations"], env=env_utf8):
        print("❌ Falha ao executar 'makemigrations'.")

    # 5. python manage.py migrate
    print("\n--- Etapa 5: Aplicando migrações (migrate) ---")
    # --- ALTERAÇÃO 2: Passar o ambiente para a chamada ---
    if not run_command([python_executable_in_venv, manage_py_path, "migrate"], env=env_utf8):
        print("❌ Falha ao executar 'migrate'.")

    # 6. python manage.py schedule_sync
    print("\n--- Etapa 6: Executando 'schedule_sync' ---")
    # --- ALTERAÇÃO 2: Passar o ambiente para a chamada ---
    if not run_command([python_executable_in_venv, manage_py_path, "schedule_sync"], env=env_utf8):
        print("❌ Falha ao executar 'schedule_sync'.")

    # 7. python manage.py create_superuser
    print("\n--- Etapa 7: Executando 'create_superuser' ---")
    # --- ALTERAÇÃO 2: Passar o ambiente para a chamada ---
    if not run_command([python_executable_in_venv, manage_py_path, "create_superuser"], env=env_utf8):
        print("❌ Falha ao executar 'create_superuser'.")


    print("\nConfiguração do projeto Django concluída!")

if __name__ == "__main__":
    main()