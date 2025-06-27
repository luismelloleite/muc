#!/usr/bin/env python
"""
Script para gerar o executável do Sistema de Controle de Visitantes
usando PyInstaller com todas as configurações necessárias para Django
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build_directories():
    """Remove diretórios de build anteriores"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Removendo {dir_name}/")
            shutil.rmtree(dir_name)
    
    # Remove arquivos .spec antigos
    for spec_file in Path('.').glob('*.spec'):
        print(f"Removendo {spec_file}")
        spec_file.unlink()

def run_collectstatic():
    """Executa collectstatic antes do build"""
    print("Executando collectstatic...")
    
    try:
        # Configurar ambiente Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portaria_muc.settings')
        
        # Carregar dotenv se existir
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        
        # Executar collectstatic
        result = subprocess.run([
            sys.executable, 'manage.py', 'collectstatic', '--noinput', '--clear'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Collectstatic executado com sucesso!")
            return True
        else:
            print(f"Erro no collectstatic: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Erro ao executar collectstatic: {e}")
        return False

def get_django_hidden_imports():
    """Retorna lista de imports hidden necessários para Django"""
    return [
        # Django core
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes', 
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        
        # Django templatetags
        'django.contrib.auth.templatetags',
        'django.contrib.contenttypes.templatetags',
        'django.contrib.sessions.templatetags',
        'django.contrib.staticfiles.templatetags',
        
        # Third party
        'rest_framework',
        'crispy_forms',
        'crispy_bootstrap5',
        'crispy_bootstrap5.templatetags',
        'dotenv',
        'psycopg2',
        'waitress',
        'whitenoise',
        'whitenoise.storage',
        
        # App específico
        'visitantes',
        'visitantes.models',
        'visitantes.views',
        'visitantes.forms',
        'visitantes.urls',
        'visitantes.admin',
        'visitantes.apps',
        'visitantes.middleware',
        'visitantes.serializers',
        'visitantes.management',
        'visitantes.management.commands',
        'visitantes.management.commands.create_superuser',
        'visitantes.management.commands.schedule_sync',
        'visitantes.management.commands.sync_visitantes',
        
        # Projeto
        'portaria_muc.settings',
        'portaria_muc.urls',
        'portaria_muc.wsgi',
        'portaria_muc.views',
        
        # Django management
        'django.core.management',
        'django.core.management.commands',
        'django.core.management.commands.migrate',
        'django.core.management.commands.runserver',
        'django.core.management.commands.collectstatic',
    ]

def get_data_files():
    """Retorna lista de arquivos de dados necessários"""
    data_files = []
    
    # Templates
    if os.path.exists('templates'):
        data_files.append(('templates', 'templates'))
    
    # Static files originais
    if os.path.exists('static'):
        data_files.append(('static', 'static'))
    
    # Staticfiles (resultado do collectstatic) - IMPORTANTE!
    if os.path.exists('staticfiles'):
        data_files.append(('staticfiles', 'staticfiles'))
    
    # Logo
    if os.path.exists('logo.png'):
        data_files.append(('logo.png', '.'))
    
    # Migrações
    for migration_dir in Path('.').rglob('migrations'):
        if migration_dir.is_dir():
            rel_path = migration_dir.relative_to('.')
            data_files.append((str(rel_path), str(rel_path)))
    
    # Arquivo .env
    if os.path.exists('.env'):
        data_files.append(('.env', '.'))
    
    # Manage.py
    if os.path.exists('manage.py'):
        data_files.append(('manage.py', '.'))
    
    # Apps Django
    django_apps = ['visitantes', 'portaria_muc']
    for app in django_apps:
        if os.path.exists(app):
            data_files.append((app, app))
    
    return data_files

def create_spec_file():
    """Cria arquivo .spec customizado para o projeto"""
    
    hidden_imports = get_django_hidden_imports()
    data_files = get_data_files()
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

# Configurações do projeto
project_name = 'Portaria MUC UFCAT'
main_script = 'main.py'
icon_path = 'logo.png' if os.path.exists('logo.png') else None

# Hidden imports para Django
hidden_imports = {hidden_imports}

# Arquivos de dados (incluindo staticfiles)
datas = {data_files}

# Análise do script principal
a = Analysis(
    [main_script],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'PIL',
        'mx',
        'django.db.backends.oracle',
        'django.db.backends.mysql',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Processamento
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Executável
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=project_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)
'''
    
    with open('Portaria MUC UFCAT.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("Arquivo 'Portaria MUC UFCAT.spec' criado!")

def run_pyinstaller():
    """Executa o PyInstaller com as configurações"""
    
    print("Executando PyInstaller...")
    
    cmd = [
        'pyinstaller',
        '--clean',
        '--noconfirm', 
        'Portaria MUC UFCAT.spec'
    ]
    
    try:
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"   {output.strip()}")
        
        return_code = process.poll()
        
        if return_code == 0:
            print("Build concluído com sucesso!")
            return True
        else:
            print(f"PyInstaller falhou com código: {return_code}")
            return False
        
    except FileNotFoundError:
        print("PyInstaller não encontrado! Instale com: pip install pyinstaller")
        return False
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return False

def post_build_cleanup():
    """Limpeza após build"""
    print("Limpeza pós-build...")
    
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("Diretório build/ removido")

def show_results():
    """Mostra resultados do build"""
    from datetime import datetime
    
    exe_path = Path('dist/Portaria MUC UFCAT.exe')
    build_end_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print("\n" + "=" * 60)
        print("BUILD CONCLUÍDO!")
        print("=" * 60)
        print(f"Executável: {exe_path.absolute()}")
        print(f"Tamanho: {size_mb:.1f} MB")
        print(f"Finalizado em: {build_end_time}")
        print("=" * 60)
    else:
        print(f"Executável não foi gerado! (Finalizado em: {build_end_time})")

def main():
    """Função principal do build"""
    print("=" * 60)
    print("  BUILD DO SISTEMA DE CONTROLE DE VISITANTES")
    print("=" * 60)
    
    # Verificações
    if not os.path.exists('manage.py'):
        print("Erro: manage.py não encontrado!")
        return
    
    if not os.path.exists('main.py'):
        print("Erro: main.py não encontrado!")
        return
    
    # Processo de build
    steps = [
        ("Limpando builds anteriores", clean_build_directories),
        ("Executando collectstatic", run_collectstatic),
        ("Criando arquivo .spec", create_spec_file),  
        ("Executando PyInstaller", run_pyinstaller),
        ("Limpeza pós-build", post_build_cleanup),
        ("Exibindo resultados", show_results),
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if step_func in [run_collectstatic, run_pyinstaller]:
            if not step_func():
                print("Build falhou!")
                return
        else:
            step_func()
    
    print("Processo concluído!")

if __name__ == "__main__":
    main()
