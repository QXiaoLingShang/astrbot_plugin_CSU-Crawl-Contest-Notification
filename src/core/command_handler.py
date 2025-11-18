"""
命令辅助类
用来管理输入命令
"""


"""

{
  "group_id_1": {
    "pushing_enabled": true,
    "tasks": [
      {"script_path": "scripts/weather.py", "cron": "0 8 * * *", "enabled": true},
      {"script_path": "scripts/news.py", "cron": "0 18 * * *", "enabled": true}
    ]
  },
  "group_id_2": {
    "pushing_enabled": false,
    "tasks": []
  }
}
"""


from functools import wraps
import re
from typing import AsyncGenerator

import traceback
import json
import asyncio
import aiofiles
from typing import Any, Optional
from datetime import datetime

# 本地模块
from ..config import GroupConfigManager
from astrbot.api.event import AstrMessageEvent, MessageEventResult, MessageChain
from astrbot.api import logger

def command_error_handler(func):
    """命令错误处理装饰器"""

    @wraps(func)
    async def wrapper(*args, **kwargs) -> AsyncGenerator[MessageEventResult, None]:
        try:
            async for result in func(*args, **kwargs):
                yield result
        except ValueError as e:
            # 参数验证错误
            event = args[1] if len(args) > 1 else None
            if event and isinstance(event, AstrMessageEvent):
                yield event.plain_result(f"参数错误: {str(e)}")
        except Exception as e:
            # 其他未预期的错误
            logger.error(f"{func.__name__} 执行出错: {str(e)}")
            logger.error(traceback.format_exc())
            event = args[1] if len(args) > 1 else None
            if event and isinstance(event, AstrMessageEvent):
                yield event.plain_result("操作执行失败，请查看日志获取详细信息")

class CommandHelper:
    def __init__(self, config_manager, context, group_config: GroupConfigManager):
        # self.config_manager = config_manager
        self.context = context
        self.group_config = group_config
        self.storage_group_config = config_manager.get_storage_root() + "/group_config.json"







    ### 对外接口 ###
    @command_error_handler
    async def set_global_task_enabled(self, event: AstrMessageEvent, boolean: bool):
        """开关推送功能"""
        # 对话id
        session_id = event.get_session_id()
        await self.group_config.set_group_settings(session_id, "pushing", boolean)
        yield event.plain_result(f"推送功能已{'开启' if boolean else '关闭'}")
    
    @command_error_handler
    async def set_task_pushing_time(self, event: AstrMessageEvent, script_path: str, time: str, session_id: str = ""):
        """
        设置推送每日时间
        :param script_path: 脚本路径（如 "scripts/weather.py"）
        :param time: 时间字符串，或者时间表达式（如 "08:00" 或 "0 8 * * *"）
        :param session_id: 会话ID（可选，默认使用事件的会话ID）
        """
        if session_id == "":
            session_id = event.get_session_id()

        # 如果为xx:xx这种格式，转化为x x * * *
        if ":" in time:
            cron_expr = f"{time.split(':')[0]} {time.split(':')[1]} * * *"   # 每天time时间推送
        else:
            cron_expr = time
        await self.group_config.set_push_task(session_id, script_path, cron_expr)
        yield event.plain_result(f"推送时间最终设置为cron表达式 {cron_expr}，并开启推送。")

    @command_error_handler
    async def set_task_enabled(self, event: AstrMessageEvent, script_path: str, enabled: bool):
        """开关推送任务"""
        # 对话id
        session_id = event.get_session_id()
        await self.group_config.set_push_task(session_id, script_path, enabled=enabled)
        yield event.plain_result(f"推送任务 {script_path} 已{'开启' if enabled else '关闭'}")
