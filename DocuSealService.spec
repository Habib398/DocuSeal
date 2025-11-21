# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file para DocuSeal Service

a = Analysis(
    ['backend/service_wrapper.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('backend/app', 'backend/app'),
        ('venv/Lib/site-packages/satcfdi/catalogs', 'satcfdi/catalogs'),
        ('venv/Lib/site-packages/satcfdi/transform/schemas', 'satcfdi/transform/schemas'),
        ('venv/Lib/site-packages/satcfdi/render', 'satcfdi/render'),
        ('Frontend/react-app/dist', 'Frontend/react-app/dist'),
    ],
    hiddenimports=[
        # Backend modules
        'backend.app',
        'backend.app.main',
        'backend.app.api_admin',
        'backend.app.api_service',
        'backend.Business',
        'backend.DB',
        # Web framework
        'uvicorn',
        'uvicorn.workers',
        'uvicorn.logging',
        'fastapi',
        'pydantic',
        'pydantic_core',
        # Database
        'psycopg2',
        'psycopg2._psycopg',
        # Utilidades
        'pdfkit',
        'bcrypt',
        'dotenv',
        # Cryptography (dependency de satcfdi)
        'cryptography',
        'cryptography.x509',
        'cryptography.hazmat',
        'cryptography.hazmat.primitives',
        'cryptography.hazmat.backends',
        # Email
        'email',
        'email.mime',
        'email.mime.text',
        'email.mime.multipart',
        'email.mime.base',
        'email.mime.application',
        # XML
        'xml',
        'xml.etree',
        'xml.etree.ElementTree',
        'xml.dom',
        'xml.dom.minidom',
        # LXML (dependency de satcfdi)
        'lxml',
        'lxml.etree',
        'lxml._elementpath',
        # SATCFDI - Modulo principal y submodulos usados
        'satcfdi',
        'satcfdi.pacs',
        'satcfdi.pacs.comerciodigital',
        'satcfdi.pacs.sat',
        'satcfdi.cfdi',
        'satcfdi.models',
        'satcfdi.models.signer',
        'satcfdi.render',
        'satcfdi.exceptions',
        'satcfdi.create',
        'satcfdi.create.cfd',
        'satcfdi.create.cfd.cfdi40',
        'satcfdi.create.cfd.pago20',
        'satcfdi.create.cfd.cartaporte31',
        'satcfdi.transform',
        'satcfdi.xelement',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DocuSealService',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # IMPORTANTE: False para no mostrar consola
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
