"""
PyInstaller hook for pkg_resources
"""
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# 收集所有pkg_resources的子模块
hiddenimports = collect_submodules('pkg_resources')

# 添加jaraco相关模块
hiddenimports.extend([
    'jaraco.text',
    'jaraco.functools',
    'jaraco.context',
    'jaraco.classes',
    'jaraco.collections',
    'importlib_metadata',
    'importlib_resources',
    'zipp',
    'more_itertools',
])

# 收集数据文件
datas = collect_data_files('pkg_resources') 