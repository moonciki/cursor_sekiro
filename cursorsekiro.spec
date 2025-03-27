# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    # 不包含resources和config，这些将作为外部目录
    datas=[],
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
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # 排除不必要的模块以减小体积，但不排除必要模块
    excludes=[
        'matplotlib', 'scipy', 'pandas', 'tkinter.test', 
        'pydoc',
        'pytest', '_pytest'
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

# 创建单个exe文件，包含所有依赖
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,       # 包含二进制文件
    a.zipfiles,
    a.datas,
    [],
    name='CursorSekiro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,      # 禁用strip，因为Windows上可能没有这个工具
    upx=True,         # 使用UPX压缩以减小体积
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,    # 隐藏控制台窗口
    icon='resources/images/icon/cursor-sekiro.ico' if os.path.exists('resources/images/icon/cursor-sekiro.ico') else None,
    uac_admin=True,
)

# 不再使用COLLECT 