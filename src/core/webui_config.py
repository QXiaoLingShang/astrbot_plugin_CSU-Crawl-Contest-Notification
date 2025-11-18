"""
配置管理模块
负责处理插件配置
"""

import sys
from astrbot.api import AstrBotConfig, logger


class ConfigManager:
    """
    WebUI的配置管理类
    """


    def __init__(self, config: AstrBotConfig):
        self.config = config
        self._pyppeteer_available = False
        self._pyppeteer_version = None
        self.base_url = self.config.get("base_url", "https://bksy.csu.edu.cn/")
    
    def get_url(self) -> str:
        """获取目标URL"""
        return self.config.get("url", "https://bksy.csu.edu.cn/tztg/cxycyjybgs.htm")
    
    def get_push_time(self) -> str:
        """获取推送时间"""
        return self.config.get("push_time", "10:00")
    
    def get_storage_root(self) -> str:
        """获取本地存储根目录"""
        return self.config.get("storage_root", "./data/plugins_data/CSU-Crawl-Contest-Notification/data/")
    
    def get_base_url(self) -> str:
        """获取基础URL"""
        return self.base_url
    
    def get_bot_qq_id(self) -> str:
        """获取机器人的qqID"""
        return self.config.get("bot_qq_id", "")
    
    def get_mode(self) -> str:
        """获取调度模式"""
        return self.config.get("mode", "daily")
    
    def get_push_interval(self) -> int:
        """获取时间间隔"""
        return self.config.get("push_interval", 60)
    
    def get_enabled_groups(self) -> list:
        """获取启用的群聊"""
        return self.config.get("enabled_groups", [])

    def get_timeout(self) -> int:
        """获取超时时间（单位秒）"""
        return self.config.get("timeout", 10)
    
    def get_group_settings(self) -> dict:
        """获取指定群组的配置"""
        return self.config.get(f"group_settings", {})
    



