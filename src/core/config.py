"""
配置管理模块
负责处理插件配置
"""

import sys
from astrbot.api import AstrBotConfig, logger


class ConfigManager:
    """
    配置管理类
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
    
    def get_storage_file(self) -> str:
        """获取本地存储路径"""
        return self.config.get("storage_file", "./data/csu_innovation_notices.csv")
    
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
