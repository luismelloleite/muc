# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

# Configurações do projeto
project_name = 'Portaria MUC UFCAT'
main_script = 'main.py'
icon_path = 'logo.png' if os.path.exists('logo.png') else None

# Hidden imports para Django
hidden_imports = ['django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles', 'django.contrib.auth.templatetags', 'django.contrib.contenttypes.templatetags', 'django.contrib.sessions.templatetags', 'django.contrib.staticfiles.templatetags', 'rest_framework', 'crispy_forms', 'crispy_bootstrap5', 'crispy_bootstrap5.templatetags', 'dotenv', 'psycopg2', 'waitress', 'whitenoise', 'visitantes', 'visitantes.models', 'visitantes.views', 'visitantes.forms', 'visitantes.urls', 'visitantes.admin', 'visitantes.apps', 'visitantes.middleware', 'visitantes.serializers', 'visitantes.management', 'visitantes.management.commands', 'visitantes.management.commands.create_superuser', 'portaria_muc.settings', 'portaria_muc.urls', 'portaria_muc.wsgi', 'portaria_muc.views', 'django.core.management', 'django.core.management.commands', 'django.core.management.commands.migrate', 'django.core.management.commands.runserver']

# Arquivos de dados
datas = [('templates', 'templates'), ('static', 'static'), ('logo.png', '.'), ('visitantes\\migrations', 'visitantes\\migrations'), ('.venv\\Lib\\site-packages\\django\\db\\migrations', '.venv\\Lib\\site-packages\\django\\db\\migrations'), ('.venv\\Lib\\site-packages\\django\\conf\\app_template\\migrations', '.venv\\Lib\\site-packages\\django\\conf\\app_template\\migrations'), ('.venv\\Lib\\site-packages\\django\\contrib\\admin\\migrations', '.venv\\Lib\\site-packages\\django\\contrib\\admin\\migrations'), ('.venv\\Lib\\site-packages\\django\\contrib\\auth\\migrations', '.venv\\Lib\\site-packages\\django\\contrib\\auth\\migrations'), ('.venv\\Lib\\site-packages\\django\\contrib\\contenttypes\\migrations', '.venv\\Lib\\site-packages\\django\\contrib\\contenttypes\\migrations'), ('.venv\\Lib\\site-packages\\django\\contrib\\flatpages\\migrations', '.venv\\Lib\\site-packages\\django\\contrib\\flatpages\\migrations'), ('.venv\\Lib\\site-packages\\django\\contrib\\redirects\\migrations', '.venv\\Lib\\site-packages\\django\\contrib\\redirects\\migrations'), ('.venv\\Lib\\site-packages\\django\\contrib\\sessions\\migrations', '.venv\\Lib\\site-packages\\django\\contrib\\sessions\\migrations'), ('.venv\\Lib\\site-packages\\django\\contrib\\sites\\migrations', '.venv\\Lib\\site-packages\\django\\contrib\\sites\\migrations'), ('.venv\\Lib\\site-packages\\rest_framework\\authtoken\\migrations', '.venv\\Lib\\site-packages\\rest_framework\\authtoken\\migrations'), ('.env', '.'), ('manage.py', '.'), ('visitantes', 'visitantes'), ('portaria_muc', 'portaria_muc')]

# Análise do script principal
a = Analysis(
    [main_script],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
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
