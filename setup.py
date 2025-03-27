"""
打包脚本，用于将CursorSekiro项目打包成可执行文件。
"""
import os
import subprocess
import shutil

def run_pyinstaller():
    """运行PyInstaller打包程序"""
    print("开始打包CursorSekiro应用...")
    
    # 清理旧的构建文件
    for dir_to_clean in ['dist', 'build', '__pycache__']:
        if os.path.exists(dir_to_clean):
            shutil.rmtree(dir_to_clean)
    
    # 构建PyInstaller命令
    pyinstaller_cmd = [
        "pyinstaller",
        "--clean",
        "--log-level=INFO",
        'cursorsekiro.spec'
    ]
    
    # 执行PyInstaller命令
    try:
        print("运行命令:", " ".join(pyinstaller_cmd))

        # 执行PyInstaller命令
        subprocess.call(pyinstaller_cmd)

        if os.path.exists('dist/CursorSekiro.exe'):
            print("\n打包完成！可执行文件位于 dist/CursorSekiro.exe")
            
            # 复制resources和config目录到dist目录
            copy_external_directories()
        else:
            print("\n打包失败！请检查错误信息")
    except Exception as e:
        print(f"执行PyInstaller时出错: {e}")

def copy_external_directories():
    """复制resources和config目录到dist目录"""
    # 复制resources目录
    if os.path.exists('resources'):
        resources_target = os.path.join('dist', 'resources')
        if os.path.exists(resources_target):
            shutil.rmtree(resources_target)
        shutil.copytree('resources', resources_target)
        print(f"已复制resources目录到{resources_target}")
    
    

if __name__ == "__main__":
    run_pyinstaller() 
