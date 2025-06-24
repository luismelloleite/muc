#!/usr/bin/env python
"""
Script para gerar o executável do Sistema de Controle de Visitantes
usando PyInstaller com todas as configurações necessárias para Django
"""

import os
import sys
import shutil
from pathlib import Path

def clean_build_directories():
    """Remove diretórios de build anteriores"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 Removendo {dir_name}/")
            shutil.rmtree(dir_name)
    
    # Remove arquivos .spec antigos
    for spec_file in Path('.').glob('*.spec'):
        print(f"🧹 Removendo {spec_file}")
        spec_file.unlink()

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
        
        # Django templatetags (reduz warnings)
        'django.contrib.auth.templatetags',
        'django.contrib.contenttypes.templatetags',
        'django.contrib.sessions.templatetags',
        'django.contrib.staticfiles.templatetags',
        
        # Third party
        'rest_framework',
        'crispy_forms',
        'crispy_bootstrap5',
        'crispy_bootstrap5.templatetags',
        'dotenv',  # Importante! python-dotenv
        'psycopg2',
        'waitress',
        'whitenoise',
        
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
    ]

def get_data_files():
    """Retorna lista de arquivos de dados necessários"""
    data_files = []
    
    # Templates
    if os.path.exists('templates'):
        data_files.append(('templates', 'templates'))
    
    # Static files  
    if os.path.exists('static'):
        data_files.append(('static', 'static'))
    
    # Logo (se existir)
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

# Arquivos de dados
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
        'tkinter',  # GUI não necessária
        'matplotlib',  # Gráficos não usados
        'numpy',  # Se não usado
        'PIL',  # Imagens não necessárias
        'mx',  # mx.DateTime warnings
        'django.db.backends.oracle',  # Oracle não usado
        'django.db.backends.mysql',  # MySQL não usado (se não usar)
        'django.db.backends.postgresql',  # PostgreSQL (manter se usar)
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
    upx=True,  # Compressão
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Manter console para debug
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,  # Logo como ícone
)
'''
    
    with open('Portaria MUC UFCAT.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("Arquivo 'Portaria MUC UFCAT.spec' criado!")
    if os.path.exists('logo.png'):
        print("Logo detectado e será usado como ícone!")

def run_pyinstaller():
    """Executa o PyInstaller com as configurações"""
    
    print("🔨 Executando PyInstaller...")
    print("   (Logs em tempo real - pode demorar alguns minutos...)\n")
    
    # Comando PyInstaller
    cmd = [
        'pyinstaller',
        '--clean',
        '--noconfirm', 
        'Portaria MUC UFCAT.spec'
    ]
    
    try:
        import subprocess
        
        # Executar com logs em tempo real
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Mostrar saída em tempo real
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"   {output.strip()}")
        
        # Verificar código de retorno
        return_code = process.poll()
        
        if return_code == 0:
            print("\nBuild concluído com sucesso!")
            return True
        else:
            print(f"\nPyInstaller falhou com código: {return_code}")
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
    
    # Manter apenas o executável em dist/
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
        if os.path.exists('logo.png'):
            print(f"Logo: Incluído como ícone")
        print("\nPróximo passo:")
        print("Use com Inno Setup para criar instalador usando o arquivo Portaria MUC UFCAT.iss")
        print("=" * 60)
    else:
        print(f"\nExecutável não foi gerado! (Finalizado em: {build_end_time})")

def main():
    """Função principal do build"""
    print("=" * 60)
    print("  BUILD DO SISTEMA DE CONTROLE DE VISITANTES")
    print("=" * 60)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('manage.py'):
        print("Erro: manage.py não encontrado!")
        return
    
    if not os.path.exists('main.py'):
        print("Erro: main.py não encontrado!")
        print("Certifique-se de ter criado o arquivo main.py")
        return
    
    # Processo de build
    steps = [
        ("Limpando builds anteriores", clean_build_directories),
        ("Criando arquivo .spec", create_spec_file),  
        ("Executando PyInstaller", run_pyinstaller),
        ("Limpeza pós-build", post_build_cleanup),
        ("Exibindo resultados", show_results),
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if step_func == run_pyinstaller:
            if not step_func():
                print("Build falhou!")
                return
        else:
            step_func()
    
    print("\nProcesso concluído!")

if __name__ == "__main__":
    main()