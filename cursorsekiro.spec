# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

# 不排除任何模块，确保所有依赖都被包含
excluded_modules = []

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # 添加资源文件，格式为 (源文件路径, 目标目录)
        ('resources/', 'resources/') if os.path.exists('resources/') else [],
        ('src/com/moonciki/cursorsekiro/', 'com/moonciki/cursorsekiro/') if os.path.exists('src/com/moonciki/cursorsekiro/') else [],
    ],
    hiddenimports=[
        'com.moonciki.cursorsekiro.app',
        'com.moonciki.cursorsekiro.utils',
        'com.moonciki.cursorsekiro.models',
        'com.moonciki.cursorsekiro.controllers',
        'com.moonciki.cursorsekiro.views',
        'doctest',
        'pdb',
        'unittest',
        'logging',
        'email',
        'html',
        'http',
        'xml',
        'xmlrpc',
        'pydoc',
        'pyrect',
        'pygetwindow',
        'traceback',
        'time',
        'PIL',
        'PIL._imaging',
        'PIL.Image',
        'pyscreeze',
        'numpy',
        'matplotlib',
        'cv2',  # OpenCV可能被用于图像处理
        'pyautogui',  # 可能被用于自动化操作
        'keyboard',  # 可能被用于键盘操作
        'mouse',  # 可能被用于鼠标操作
        # 添加pkg_resources相关依赖
        'pkg_resources',
        'pkg_resources.py2_warn',
        'jaraco',
        'jaraco.text',
        'jaraco.functools',
        'jaraco.context',
        'jaraco.classes',
        'jaraco.collections',
        'importlib_metadata',
        'importlib_resources',
        'zipp',
        'more_itertools',
        'setuptools',
        'packaging',
        'packaging.version',
        'packaging.specifiers',
        'packaging.requirements',
        'appdirs',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excluded_modules,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 不过滤二进制文件，确保所有必要的DLL都被包含
# a.binaries = [x for x in a.binaries if not (x[0].startswith('msvcp') and not x[0].endswith('140.dll'))]

pyz = PYZ(
    a.pure, 
    a.zipped_data,
    cipher=block_cipher
)

# 只创建目录模式的可执行文件
exe = EXE(
    pyz,
    a.scripts,
    [],  # 不包含二进制文件在exe中
    exclude_binaries=True,  # 排除二进制文件，放在外部目录
    name='CursorSekiro',
    debug=True,  # 启用调试信息
    bootloader_ignore_signals=False,
    strip=False,  # 不移除调试符号，便于排错
    upx=False,    # 禁用UPX压缩，避免兼容性问题
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 保持控制台可见，便于查看错误
    icon='resources/images/icon/cursor-sekiro.ico' if os.path.exists('resources/images/icon/cursor-sekiro.ico') else None,
    uac_admin=True,
)

# 创建包含所有文件的目录
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,  # 禁用UPX压缩
    upx_exclude=[],
    name='CursorSekiro',
) 