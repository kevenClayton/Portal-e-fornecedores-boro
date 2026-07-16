# -*- mode: python ; coding: utf-8 -*-
# Gere o .exe no Windows:
#   pyinstaller --noconfirm portal.spec

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=['src'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'portal_fornecedores',
        'portal_fornecedores.main',
        'portal_fornecedores.config.settings',
        'portal_fornecedores.browser.manager',
        'portal_fornecedores.browser.pages.login_page',
        'portal_fornecedores.browser.pages.cargas_page',
        'portal_fornecedores.browser.pages.detalhes_carga_page',
        'portal_fornecedores.browser.pages.vinculacao_page',
        'portal_fornecedores.database.connection',
        'portal_fornecedores.database.repositories.dados_repository',
        'portal_fornecedores.services.rota_service',
        'portal_fornecedores.services.vinculacao_service',
        'portal_fornecedores.services.email_service',
        'mysql.connector',
        'playwright',
        'playwright.sync_api',
        'pandas',
        'bs4',
        'lxml',
        'pydantic',
        'pydantic_settings',
        'dotenv',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['FreeSimpleGUI', 'tkinter', 'matplotlib', 'scipy', 'PIL'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PortalFornecedores',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,   # mantém terminal para ver o status
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
