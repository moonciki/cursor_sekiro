#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cursor进程关闭工具

这个模块提供了安全地关闭Cursor进程的功能。
它会尝试优雅地关闭进程，如果失败则强制终止。
"""

import os
import sys
import time
import psutil
from typing import List, Optional
from com.moonciki.cursorsekiro.logger import Logger
from com.moonciki.cursorsekiro.utils.cursor_constants import CursorConstants

class CursorProcessKiller:
    """用于管理和关闭Cursor进程的类"""
    
    MAX_WAIT_TIME = 5  # 等待进程关闭的最大秒数

    @staticmethod
    def get_cursor_processes() -> List[psutil.Process]:
        """
        获取所有运行中的Cursor相关进程

        Returns:
            List[psutil.Process]: Cursor相关进程列表
        """
        cursor_processes = []
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc.info['name'] in CursorConstants.CURSOR_PROCESS_NAMES:
                    cursor_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return cursor_processes

    @staticmethod
    def terminate_process(process: psutil.Process) -> bool:
        """
        尝试终止单个进程

        Args:
            process: 要终止的进程

        Returns:
            bool: 是否成功终止进程
        """
        try:
            process_name = process.name()
            pid = process.pid
            
            # 首先尝试正常终止
            process.terminate()
            
            # 等待进程结束
            try:
                process.wait(timeout=3)
                Logger.info(f"终止进程: {process_name} (PID: {pid})")
                return True
            except psutil.TimeoutExpired:
                # 如果超时，强制结束进程
                process.kill()
                Logger.warn(f"强制终止: {process_name} (PID: {pid})")
                return True
                
        except psutil.NoSuchProcess:
            Logger.info(f"进程不存在: {process_name} (PID: {pid})")
            return True
        except Exception as e:
            Logger.error(f"终止失败: {str(e)}", e)
            return False

    @staticmethod
    def close_cursor() -> bool:
        """
        关闭所有Cursor相关进程

        Returns:
            bool: 是否成功关闭所有进程
        """
        cursor_processes = CursorProcessKiller.get_cursor_processes()
        
        if not cursor_processes:
            Logger.info("未发现Cursor进程")
            return True
            
        success = True
        for process in cursor_processes:
            if not CursorProcessKiller.terminate_process(process):
                success = False
                
        # 最后验证
        remaining_processes = CursorProcessKiller.get_cursor_processes()
        if remaining_processes:
            process_list = ", ".join([f"{p.name()} (PID: {p.pid})" for p in remaining_processes])
            Logger.error(f"未能关闭的进程: {process_list}")
            return False
            
        Logger.info("所有Cursor进程已关闭")
        return success

def main() -> None:
    """主函数"""
    try:
        if CursorProcessKiller.close_cursor():
            Logger.info("完成")
            sys.exit(0)
        else:
            Logger.error("无法完全关闭Cursor")
            sys.exit(1)
    except Exception as e:
        Logger.error("发生错误", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
