# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# 收集 tkinter 相关的所有数据文件
tkinter_datas = []
if not any('excludes=tkinter' in arg for arg in sys.argv):
    try:
        from PyInstaller.utils.hooks import collect_data_files
        tkinter_datas = collect_data_files('tkinter')
    except:
        pass

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    # 添加 tkinter 数据文件
    datas=tkinter_datas,
    hiddenimports=[
        'com.moonciki.cursorsekiro.app',
        'com.moonciki.cursorsekiro.utils',
        'com.moonciki.cursorsekiro.models',
        'com.moonciki.cursorsekiro.controllers',
        'com.moonciki.cursorsekiro.views',
        'PIL',
        'PIL._imaging',
        'PIL.Image',
        'pyscreeze',
        'numpy',
        'cv2',
        'pyautogui',
        'keyboard',
        'mouse',
        'pkg_resources',
        'email',
        'xml',
        'xml.etree',
        'xml.etree.ElementTree',
        'http',
        'http.client',
        'urllib',
        'urllib.request',
        'doctest',
        'pyrect',
        'pygetwindow',
        'pdb',
        'unittest',
        # 如果你的应用使用 tkinter，请添加以下内容
        'tkinter',
        'tkinter.ttk',
        '_tkinter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # 如果你的应用不使用 tkinter，可以将其排除
    excludes=[
        'matplotlib', 'scipy', 'pandas', 'tkinter.test', 
        'pydoc',
        'pytest', '_pytest'
        # 如果你的应用不使用 tkinter，取消下面这行的注释
        # 'tkinter', '_tkinter', 'Tkinter'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure, 
    a.zipped_data,
    cipher=block_cipher
)

# 创建exe文件，但不包含所有依赖
exe = EXE(
    pyz,
    a.scripts,
    [],  # 不包含二进制文件和数据
    exclude_binaries=True,  # 排除二进制文件，使用目录方式打包
    name='CursorSekiro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='resources/images/icon/cursor-sekiro.ico' if os.path.exists('resources/images/icon/cursor-sekiro.ico') else None,
    uac_admin=True,
)

# 使用COLLECT创建目录结构
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CursorSekiro',
)