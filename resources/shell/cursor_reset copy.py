import os
import json
import uuid
import shutil
import winreg
import ctypes
import datetime
import secrets
from pathlib import Path
from typing import Dict, Optional, Tuple

# 颜色常量
class Colors:
    RED = "\033[31m"
    GREEN = "\033[32m" 
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    NC = "\033[0m"

class CursorReset:
    def __init__(self):
        """初始化CursorReset类"""
        self.storage_file = os.path.join(os.getenv('APPDATA'), 'Cursor', 'User', 'globalStorage', 'storage.json')
        self.backup_dir = os.path.join(os.getenv('APPDATA'), 'Cursor', 'User', 'globalStorage', 'backups')
        self.updater_path = os.path.join(os.getenv('LOCALAPPDATA'), 'cursor-updater')
        self.registry_backup_dir = os.path.join(self.backup_dir, 'registry')

    def is_admin(self) -> bool:
        """检查是否具有管理员权限"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def generate_ids(self) -> Dict[str, str]:
        """生成新的ID"""
        # 生成auth0|user_前缀的十六进制
        prefix = "auth0|user_".encode('utf-8').hex()
        # 生成32字节的随机十六进制
        random_part = secrets.token_hex(32)
        
        return {
            'machine_id': f"{prefix}{random_part}",
            'mac_machine_id': str(uuid.uuid4()),
            'uuid': str(uuid.uuid4()),
            'sqm_id': "{" + str(uuid.uuid4()).upper() + "}"
        }

    def backup_config(self) -> None:
        """备份配置文件"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

        if os.path.exists(self.storage_file):
            print(f"{Colors.GREEN}[信息]{Colors.NC} 正在备份配置文件...")
            backup_name = f"storage.json.backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(self.storage_file, os.path.join(self.backup_dir, backup_name))

    def backup_registry(self) -> None:
        """备份注册表"""
        try:
            if not os.path.exists(self.registry_backup_dir):
                os.makedirs(self.registry_backup_dir)
                
            backup_file = os.path.join(
                self.registry_backup_dir,
                f"MachineGuid_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.reg"
            )
            
            # 使用reg.exe导出注册表
            cmd = f'reg export "HKLM\\SOFTWARE\\Microsoft\\Cryptography" "{backup_file}" /y'
            result = os.system(cmd)
            
            if result == 0:
                print(f"{Colors.GREEN}[信息]{Colors.NC} 注册表备份成功: {backup_file}")
            else:
                print(f"{Colors.YELLOW}[警告]{Colors.NC} 注册表备份失败")
                
        except Exception as e:
            print(f"{Colors.RED}[错误]{Colors.NC} 备份注册表失败: {str(e)}")

    def show_file_tree(self) -> None:
        """显示文件树结构"""
        print(f"\n{Colors.GREEN}[信息]{Colors.NC} 文件结构:")
        print(f"{Colors.BLUE}{os.getenv('APPDATA')}\\Cursor\\User{Colors.NC}")
        print("├── globalStorage")
        print("│   ├── storage.json (已修改)")
        print("│   └── backups")
        
        # 显示备份文件
        if os.path.exists(self.backup_dir):
            files = os.listdir(self.backup_dir)
            for i, file in enumerate(files):
                prefix = "│   " if i < len(files) - 1 else "    "
                print(f"│       └── {file}")
        else:
            print("│       └── (空)")

    def show_manual_guide(self) -> None:
        """显示手动操作指南"""
        print(f"\n{Colors.YELLOW}[手动操作指南]{Colors.NC}")
        print("如果自动操作失败，请按以下步骤手动操作：")
        print("\n1. 禁用自动更新：")
        print(f"   - 创建文件：{self.updater_path}")
        print("   - 右键属性设置为只读")
        
        print("\n2. 修改注册表：")
        print("   - 打开注册表编辑器(regedit)")
        print("   - 导航到：HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Cryptography")
        print("   - 修改 MachineGuid 值")

    def update_machine_guid(self) -> bool:
        """更新注册表中的MachineGuid"""
        try:
            registry_path = r"SOFTWARE\Microsoft\Cryptography"
            new_guid = str(uuid.uuid4())
            
            # 备份当前值
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, winreg.KEY_READ) as key:
                    current_guid = winreg.QueryValueEx(key, "MachineGuid")[0]
                    print(f"{Colors.GREEN}[信息]{Colors.NC} 当前MachineGuid: {current_guid}")
            except:
                print(f"{Colors.YELLOW}[警告]{Colors.NC} 无法读取当前MachineGuid")

            # 更新值
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "MachineGuid", 0, winreg.REG_SZ, new_guid)
                print(f"{Colors.GREEN}[信息]{Colors.NC} MachineGuid已更新为: {new_guid}")
            return True
        except Exception as e:
            print(f"{Colors.RED}[错误]{Colors.NC} 更新MachineGuid失败: {str(e)}")
            return False

    def update_config(self) -> bool:
        """更新配置文件"""
        try:
            if not os.path.exists(self.storage_file):
                print(f"{Colors.RED}[错误]{Colors.NC} 未找到配置文件: {self.storage_file}")
                print(f"{Colors.YELLOW}[提示]{Colors.NC} 请先安装并运行一次Cursor后再使用此脚本")
                return False

            # 读取并更新配置
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            new_ids = self.generate_ids()
            config['telemetry.machineId'] = new_ids['machine_id']
            config['telemetry.macMachineId'] = new_ids['mac_machine_id']
            config['telemetry.devDeviceId'] = new_ids['uuid']
            config['telemetry.sqmId'] = new_ids['sqm_id']

            # 写入更新后的配置
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)

            print(f"\n{Colors.GREEN}[信息]{Colors.NC} 配置更新成功:")
            print(f"{Colors.BLUE}[调试]{Colors.NC} machineId: {new_ids['machine_id']}")
            print(f"{Colors.BLUE}[调试]{Colors.NC} macMachineId: {new_ids['mac_machine_id']}")
            print(f"{Colors.BLUE}[调试]{Colors.NC} devDeviceId: {new_ids['uuid']}")
            print(f"{Colors.BLUE}[调试]{Colors.NC} sqmId: {new_ids['sqm_id']}")
            return True

        except Exception as e:
            print(f"{Colors.RED}[错误]{Colors.NC} 更新配置失败: {str(e)}")
            return False

    def disable_auto_update(self) -> None:
        """禁用自动更新功能"""
        try:
            if os.path.exists(self.updater_path):
                if os.path.isfile(self.updater_path):
                    print(f"{Colors.GREEN}[信息]{Colors.NC} 已存在更新阻止文件")
                    return
                shutil.rmtree(self.updater_path)

            # 创建阻止文件
            with open(self.updater_path, 'w') as f:
                pass

            # 设置只读属性
            os.chmod(self.updater_path, 0o444)
            print(f"{Colors.GREEN}[信息]{Colors.NC} 已成功禁用自动更新")

        except Exception as e:
            print(f"{Colors.RED}[错误]{Colors.NC} 禁用自动更新失败: {str(e)}")

    def run(self) -> None:
        """运行主程序"""
        if not self.is_admin():
            print(f"{Colors.RED}[错误]{Colors.NC} 请以管理员权限运行此脚本")
            input("按回车键退出...")
            return

        print(f"{Colors.BLUE}Cursor ID 重置工具{Colors.NC}")
        print("=" * 50)

        # 备份所有内容
        self.backup_config()
        self.backup_registry()
        
        # 更新配置
        if self.update_config():
            self.update_machine_guid()

            print(f"\n{Colors.YELLOW}[询问]{Colors.NC} 是否要禁用Cursor自动更新功能？")
            print("0) 否 - 保持默认设置 (按回车键)")
            print("1) 是 - 禁用自动更新")
            print("2) 显示手动操作指南")
            
            choice = input("请输入选项 (0): ").strip()
            if choice == "1":
                self.disable_auto_update()
            elif choice == "2":
                self.show_manual_guide()

        # 显示文件树
        self.show_file_tree()
        
        print("\n" + "=" * 50)
        input("按回车键退出...")

if __name__ == "__main__":
    cursor_reset = CursorReset()
    cursor_reset.run()
