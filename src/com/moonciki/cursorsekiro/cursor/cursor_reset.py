import json
import os
import uuid
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
import winreg
from typing import Dict, Optional, Tuple
from ..logger import Logger  # 添加Logger导入

class CursorReset:
    """用于重置Cursor编辑器标识符的工具类"""

    # 文件路径常量
    STORAGE_FILE = os.path.join(os.getenv('APPDATA'), 'Cursor', 'User', 'globalStorage', 'storage.json')
    BACKUP_DIR = os.path.join(os.getenv('APPDATA'), 'Cursor', 'User', 'globalStorage', 'backups')

    @staticmethod
    def create_backup_dir() -> None:
        """创建备份目录"""
        if not os.path.exists(CursorReset.BACKUP_DIR):
            os.makedirs(CursorReset.BACKUP_DIR)

    @staticmethod
    def backup_config() -> None:
        """备份现有配置文件"""
        if os.path.exists(CursorReset.STORAGE_FILE):
            Logger.info("正在备份配置文件...")
            backup_name = f"storage.json.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(CursorReset.STORAGE_FILE, os.path.join(CursorReset.BACKUP_DIR, backup_name))

    @staticmethod
    def generate_machine_id() -> str:
        """生成新的机器ID"""
        prefix = "auth0|user_"
        prefix_hex = prefix.encode('utf-8').hex()
        random_hex = uuid.uuid4().hex
        return f"{prefix_hex}{random_hex[:64-len(prefix_hex)]}"

    @staticmethod
    def generate_ids() -> Dict[str, str]:
        """生成所有需要的ID"""
        ids_dict = {
            'machineId': CursorReset.generate_machine_id(),
            'macMachineId': str(uuid.uuid4()),
            'devDeviceId': str(uuid.uuid4()),
            'sqmId': f"{{{str(uuid.uuid4()).upper()}}}"
        }
        
        return ids_dict

    @staticmethod
    def update_machine_guid_reg() -> bool:
        """更新注册表中的MachineGuid"""
        try:
            registry_path = r"SOFTWARE\Microsoft\Cryptography"
            
            # 备份当前值
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, 
                                  winreg.KEY_READ) as key:
                    original_guid = winreg.QueryValueEx(key, "MachineGuid")[0]
                    Logger.info(f"当前MachineGuid: {original_guid}")
            except Exception:
                original_guid = None
                Logger.warn("无法读取当前MachineGuid")

            new_guid = str(uuid.uuid4())
            # 更新注册表
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, 
                              winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "MachineGuid", 0, winreg.REG_SZ, new_guid)

            Logger.info(f"注册表更新成功: {new_guid}")
            return True

        except Exception as e:
            Logger.error(f"更新注册表失败: ", e)
            return False

    @staticmethod
    def update_config(new_ids: Dict[str, str]) -> bool:
        """更新配置文件"""
        try:
            if not os.path.exists(CursorReset.STORAGE_FILE):
                Logger.error("未找到配置文件")
                return False

            with open(CursorReset.STORAGE_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 更新配置
            config['telemetry.machineId'] = new_ids['machineId']
            config['telemetry.macMachineId'] = new_ids['macMachineId']
            config['telemetry.devDeviceId'] = new_ids['devDeviceId']
            config['telemetry.sqmId'] = new_ids['sqmId']

            # 写入新配置
            with open(CursorReset.STORAGE_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)

            Logger.info("配置文件更新成功")
            return True

        except Exception as e:
            Logger.error(f"更新配置失败: ", e)
            raise e

    @staticmethod
    def disable_auto_update() -> bool:
        """禁用Cursor的自动更新功能"""
        updater_path = os.path.join(os.getenv('LOCALAPPDATA'), 'cursor-updater')
        
        try:
            # 如果updater_path已经是文件且存在，说明已经禁用了自动更新
            if os.path.isfile(updater_path):
                Logger.info("已创建阻止更新文件，无需再次阻止")
                return True

            # 如果是目录，删除它
            if os.path.isdir(updater_path):
                shutil.rmtree(updater_path)
                Logger.info("成功删除 cursor-updater 目录")

            # 创建阻止文件
            with open(updater_path, 'w') as f:
                pass
            
            # 设置只读属性
            os.chmod(updater_path, 0o444)  # 设置为只读权限
            
            Logger.info("成功禁用自动更新")
            return True

        except Exception as e:
            Logger.error(f"禁用自动更新失败: ", e)
            Logger.warn("请手动操作：")
            Logger.info(f"1. 删除目录（如果存在）：{updater_path}")
            Logger.info(f"2. 创建空文件：{updater_path}")
            Logger.info("3. 将文件设置为只读")
            return False

    @staticmethod
    def reset_cursor(disable_update: bool = True) -> None:
        """
        执行Cursor重置流程
        
        Args:
            disable_update: 是否禁用自动更新，默认为False
        """
        try:
            # 创建备份目录
            CursorReset.create_backup_dir()
            
            # 备份当前配置
            CursorReset.backup_config()
            
            # 生成新ID
            new_ids = CursorReset.generate_ids()
            
            # 更新配置文件
            CursorReset.update_config(new_ids)
            # 更新注册表
            
            # 生成新GUID
            CursorReset.update_machine_guid_reg()
            Logger.info("Cursor重置完成")
            
            # 根据参数决定是否禁用自动更新
            if disable_update:
                Logger.info("正在禁用自动更新...")
                CursorReset.disable_auto_update()
            else:
                Logger.info("保持默认设置，不禁用自动更新")
            
                
        except Exception as e:
            Logger.error(f"发生未知错误: ", e)
            raise e

if __name__ == "__main__":
    
    CursorReset.reset_cursor()
