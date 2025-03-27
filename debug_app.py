"""
调试脚本，用于在打包后调试应用程序。
"""
import os
import sys
import subprocess
import time

def debug_packaged_app():
    """调试打包后的应用程序"""
    print("正在调试打包后的应用程序...")
    
    # 确定应用程序路径
    app_path = os.path.join('dist', 'CursorSekiro', 'CursorSekiro.exe')
    if not os.path.exists(app_path):
        print(f"错误: 找不到应用程序 {app_path}")
        return False
    
    # 创建日志目录
    log_dir = os.path.join('dist', 'CursorSekiro', 'debug_logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 创建日志文件路径
    log_file = os.path.join(log_dir, f'debug_{time.strftime("%Y%m%d_%H%M%S")}.log')
    
    # 设置环境变量，启用更多调试信息
    env = os.environ.copy()
    env['PYTHONFAULTHANDLER'] = '1'  # 启用Python故障处理程序
    env['PYTHONUTF8'] = '1'  # 强制UTF-8编码
    env['PYTHONIOENCODING'] = 'utf-8'  # 设置IO编码
    
    # 运行应用程序并重定向输出到日志文件
    print(f"正在运行应用程序，日志将保存到 {log_file}")
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"=== 调试会话开始于 {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")
        
        try:
            process = subprocess.Popen(
                [app_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            
            # 实时读取输出并写入日志
            while True:
                stdout_line = process.stdout.readline()
                stderr_line = process.stderr.readline()
                
                if stdout_line:
                    print(f"[输出] {stdout_line.strip()}")
                    f.write(f"[输出] {stdout_line}")
                    f.flush()
                
                if stderr_line:
                    print(f"[错误] {stderr_line.strip()}")
                    f.write(f"[错误] {stderr_line}")
                    f.flush()
                
                # 检查进程是否结束
                if process.poll() is not None:
                    # 读取剩余输出
                    stdout_rest, stderr_rest = process.communicate()
                    
                    if stdout_rest:
                        print(f"[输出] {stdout_rest.strip()}")
                        f.write(f"[输出] {stdout_rest}")
                    
                    if stderr_rest:
                        print(f"[错误] {stderr_rest.strip()}")
                        f.write(f"[错误] {stderr_rest}")
                    
                    break
            
            exit_code = process.returncode
            f.write(f"\n=== 应用程序退出，退出代码: {exit_code} ===\n")
            print(f"应用程序已退出，退出代码: {exit_code}")
            
            return exit_code == 0
            
        except Exception as e:
            error_msg = f"调试过程中出错: {e}"
            print(error_msg)
            f.write(f"\n{error_msg}\n")
            return False

if __name__ == "__main__":
    success = debug_packaged_app()
    if success:
        print("\n调试成功！应用程序正常退出。")
    else:
        print("\n调试失败！应用程序异常退出。") 