"""
邮箱配置常量模块。
"""
import os
import json
from typing import Dict, Any, Optional
from com.moonciki.cursorsekiro.logger import Logger
from com.moonciki.cursorsekiro.utils.cursor_constants import CursorConstants

class EmailConstants:
    """
    邮箱配置常量类，用于管理邮箱相关的配置信息。
    """
    
    # 配置文件路径
    CONFIG_PATH = CursorConstants.CONFIG_FILE_PATH
    
    # 默认邮箱域名
    DEFAULT_DOMAIN = "@126.com"
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """
        获取邮箱配置。
        
        Returns:
            包含邮箱配置的字典
        """
        try:
            # 确保配置目录存在
            os.makedirs(os.path.dirname(cls.CONFIG_PATH), exist_ok=True)
            
            if os.path.exists(cls.CONFIG_PATH):
                with open(cls.CONFIG_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            Logger.info("首次使用，请配置邮箱")
            return {}
    
    @classmethod
    def save_config(cls, email_prefix: str, _: str = "", disable_auto_update: bool = True, cursor_exe_path: str = None) -> bool:
        """
        保存邮箱配置。
        
        Args:
            email_prefix: 邮箱前缀
            _: 保留参数，用于兼容性
            disable_auto_update: 是否禁用自动更新
            cursor_exe_path: Cursor.exe路径，如果为None则不更新此项
            
        Returns:
            保存是否成功
        """
        try:
            # 确保配置目录存在
            os.makedirs(os.path.dirname(cls.CONFIG_PATH), exist_ok=True)
            
            # 读取现有配置
            config = cls.get_config()
            
            # 更新配置
            config['email_prefix'] = email_prefix
            config['email_suffix'] = cls.DEFAULT_DOMAIN
            config['disable_auto_update'] = disable_auto_update
            
            # 如果提供了Cursor.exe路径，则更新
            if cursor_exe_path is not None:
                config['cursor_exe_path'] = cursor_exe_path
            
            with open(cls.CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            Logger.info("配置已保存")
            return True
        except Exception as e:
            Logger.error(f"保存配置失败: ", e)
            return False
    
    @classmethod
    def get_email(cls) -> Optional[str]:
        """
        获取完整邮箱地址。
        
        Returns:
            完整邮箱地址，如果未配置则返回None
        """
        config = cls.get_config()
        email_prefix = config.get('email_prefix')
        if email_prefix:
            return f"{email_prefix}{cls.DEFAULT_DOMAIN}"
        return None
    
    @classmethod
    def get_email_prefix(cls) -> str:
        """
        获取邮箱前缀。
        
        Returns:
            邮箱前缀，如果未配置则返回空字符串
        """
        return cls.get_config().get('email_prefix', '')
    
    @classmethod
    def is_config_saved(cls) -> bool:
        """
        检查是否已保存邮箱配置。
        
        Returns:
            是否已保存配置
        """
        if not os.path.exists(cls.CONFIG_PATH):
            return False
            
        config = cls.get_config()
        email_prefix = config.get('email_prefix', '')
        
        return bool(email_prefix and email_prefix.strip())
    
    @classmethod
    def get_disable_auto_update(cls) -> bool:
        """
        获取是否禁用自动更新设置。
        
        Returns:
            是否禁用自动更新，默认为True
        """
        return cls.get_config().get('disable_auto_update', True)
    
    @classmethod
    def get_cursor_exe_path(cls) -> str:
        """
        获取Cursor.exe路径。
        
        Returns:
            Cursor.exe路径，如果未配置则返回默认路径
        """
        path = cls.get_config().get('cursor_exe_path')
        if path and os.path.exists(path):
            return path
        return CursorConstants.CURSOR_EXE_PATH
    
    @classmethod
    def save_cursor_exe_path(cls, cursor_exe_path: str) -> bool:
        """
        保存Cursor.exe路径。
        
        Args:
            cursor_exe_path: Cursor.exe路径
            
        Returns:
            保存是否成功
        """
        try:
            # 读取现有配置
            config = cls.get_config()
            
            # 更新Cursor.exe路径
            config['cursor_exe_path'] = cursor_exe_path
            
            # 保存配置
            with open(cls.CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            Logger.info(f"Cursor安装路径已保存: {cursor_exe_path}")
            return True
        except Exception as e:
            Logger.error(f"保存Cursor.exe路径失败: {str(e)}")
            return False 