"""
自动调度器模块
负责定时任务
"""


import asyncio
from datetime import datetime, timedelta
from astrbot.api import logger


class AutoScheduler:
    """自动调度器"""

    def __init__(
        self,
        config_manager,
        NoticeDataHandler,
        ReportGenerator,
        html_render_func,
        bot_manager,
        ):
        self.bot_manager = bot_manager
        self.config_manager = config_manager
        self.NoticeDataHandler = NoticeDataHandler
        self.ReportGenerator = ReportGenerator
        self.html_render_func = html_render_func
    
    def _get_platform_id(self):
        """获取平台ID"""
        try:
            if hasattr(self.bot_manager, "_context") and self.bot_manager._context:
                context = self.bot_manager._context
                if hasattr(context, "platform_manager") and hasattr(
                    context.platform_manager, "platform_insts"
                ):
                    platforms = context.platform_manager.platform_insts
                    for platform in platforms:
                        if hasattr(platform, "metadata") and hasattr(
                            platform.metadata, "id"
                        ):
                            platform_id = platform.metadata.id
                            return platform_id
            return "aiocqhttp"  # 默认值
        except Exception:
            return "aiocqhttp"  # 默认值