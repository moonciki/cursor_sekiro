"""
打包脚本，用于将CursorSekiro项目打包成可执行文件。
"""
import os
import subprocess
import shutil
import sys

def run_pyinstaller():
    """
    运行PyInstaller打包程序。
    """
    print("开始打包CursorSekiro应用...")
    
    # 确保输出目录存在
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # 确保PyInstaller缓存被清理
    if os.path.exists('__pycache__'):
        shutil.rmtree('__pycache__')
    
    # 创建hooks目录（如果不存在）
    if not os.path.exists('hooks'):
        os.makedirs('hooks')
        # 创建hook-pkg_resources.py文件
        with open('hooks/hook-pkg_resources.py', 'w') as f:
            f.write('''"""
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
''')
    
    # 构建PyInstaller命令 - 使用更多调试选项
    pyinstaller_cmd = [
        "pyinstaller",
        "--clean",  # 清理PyInstaller缓存
        "--log-level=DEBUG",  # 使用DEBUG日志级别
        "--additional-hooks-dir=hooks",  # 添加自定义hooks目录
        'cursorsekiro.spec'
    ]
    
    # 执行PyInstaller命令
    try:
        print("运行命令:", " ".join(pyinstaller_cmd))
        result = subprocess.run(pyinstaller_cmd, capture_output=True, text=True)
        
        # 输出详细信息
        print("\n--- PyInstaller 标准输出 ---")
        print(result.stdout)
        
        if result.stderr:
            print("\n--- PyInstaller 错误输出 ---")
            print(result.stderr)
        
        if os.path.exists('dist/CursorSekiro'):
            print("\n打包完成！可执行文件位于 dist/CursorSekiro 目录")
            
            # 创建启动脚本
            create_launcher_script()
        else:
            print("\n打包失败！请检查错误信息")
    except Exception as e:
        print(f"执行PyInstaller时出错: {e}")

def create_launcher_script():
    """创建一个启动脚本，用于捕获错误"""
    launcher_path = os.path.join('dist', 'CursorSekiro', 'launch.bat')
    with open(launcher_path, 'w') as f:
        f.write('@echo off\n')
        f.write('echo 正在启动CursorSekiro...\n')
        f.write('CursorSekiro.exe\n')
        f.write('if %ERRORLEVEL% NEQ 0 (\n')
        f.write('  echo 程序异常退出，错误代码: %ERRORLEVEL%\n')
        f.write('  echo 请查看logs目录下的日志文件\n')
        f.write('  pause\n')
        f.write(')\n')
    
    print(f"创建了启动脚本: {launcher_path}")
    print("如果应用闪退，请使用此脚本启动，以查看错误信息")

if __name__ == "__main__":
    # 运行PyInstaller打包
    run_pyinstaller() 
