"""
测试脚本，用于在打包前测试应用程序是否能正常运行。
"""
import os
import sys
import subprocess

def run_app():
    """运行应用程序并捕获输出"""
    print("正在测试应用程序...")
    
    # 设置环境变量，启用Python的详细错误信息
    env = os.environ.copy()
    env['PYTHONFAULTHANDLER'] = '1'
    
    # 运行应用程序
    try:
        result = subprocess.run(
            [sys.executable, 'src/main.py'],
            capture_output=True,
            text=True,
            env=env
        )
        
        # 输出结果
        print("\n--- 标准输出 ---")
        print(result.stdout)
        
        print("\n--- 错误输出 ---")
        print(result.stderr)
        
        print(f"\n退出代码: {result.returncode}")
        
        return result.returncode == 0
    except Exception as e:
        print(f"测试过程中出错: {e}")
        return False

if __name__ == "__main__":
    success = run_app()
    if success:
        print("\n测试成功！应用程序可以正常运行。")
    else:
        print("\n测试失败！请检查错误信息。") 