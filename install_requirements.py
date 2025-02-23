import subprocess
import sys

def install_requirements():
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("依赖安装成功！")
    except subprocess.CalledProcessError as e:
        print(f"安装过程中出现错误：{e}")
    except Exception as e:
        print(f"发生未知错误：{e}")

if __name__ == '__main__':
    install_requirements() 