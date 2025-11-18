"""
群组配置类
用来管理每个群组的独立配置
暂未实装
"""

# 标准库
import os
import traceback

# 三方库
import aiofiles
import json
from typing import Any

# 本地模块
from astrbot.api import logger
from ..core import ConfigManager






class GroupConfigManager:
    def __init__(self, config_manager, context):
        # self.config_manager = config_manager
        self.context = context
        self.storage_group_config = config_manager.get_storage_root() + "/group_config.json"
        self._init_storage()
    
    ### 私有方法 ###
    def _init_storage(self) -> None:
        """初始化群组配置文件"""
        # 检查文件是否存在
        if not os.path.exists(self.storage_group_config):
            # 如果不存在，创建空文件
            os.makedirs(os.path.dirname(self.storage_group_config), exist_ok=True)
            with open(self.storage_group_config, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=4)


    def _is_valid_cron(self, cron_expr: str) -> bool:
        """验证cron表达式格式是否正确"""

        # 正则匹配cron表达式格式
        import re
        cron_pattern = r"^(\d+|\*)\s+(\d+|\*)\s+(\d+|\*)\s+(\d+|\*)\s+(\d+|\*)\s+(\d+|\*)$"
        return re.match(cron_pattern, cron_expr) is not None
            

    ### 对外方法 ###
    # 群组基础配置
    async def set_group_settings(self, group_id: str, setting_key: str, setting_value: Any):
        """设置群组的独立配置，修改某个群的某个配置项"""
        
        try:
            # 异步打开storage_group_config指向的文件
            async with aiofiles.open(self.storage_group_config, "r+", encoding="utf-8") as f:
                # 读取文件内容
                content = await f.read()
                # 解析为 JSON 对象
                group_settings = json.loads(content) if content else {}
                # 更新群组配置
                if group_id not in group_settings:
                    group_settings[group_id] = {}
                group_settings[group_id][setting_key] = setting_value
                # 写入文件
                await f.seek(0)
                await f.write(json.dumps(group_settings, ensure_ascii=False, indent=4))
                await f.truncate()
        except Exception as e:
            logger.error(f"尝试将群组{group_id}的{setting_key}配置为{setting_value}出错: {str(e)}")
            logger.error(traceback.format_exc())
            raise e

    async def get_group_settings(self, group_id: str) -> dict:
        """获取群组的独立配置（存储于本地配置文件）"""
        try:
            # 异步打开storage_group_config指向的文件
            async with aiofiles.open(self.storage_group_config, "r", encoding="utf-8") as f:
                # 读取文件内容
                content = await f.read()
                # 解析为 JSON 对象
                group_settings = json.loads(content) if content else {}
                # 返回群组配置
                return group_settings.get(group_id, {})
        except Exception as e:
            logger.error(f"尝试获取群组{group_id}的配置出错: {str(e)}")
            logger.error(traceback.format_exc())
            raise e

        # self.unified_msg_origin = str(self.session)
        # """统一的消息来源字符串。格式为 platform_name:message_type:session_id"""


    # 群组推送任务管理
    async def set_push_task(self, session_id: str, script_path: str, cron_expr: str = "-1", enabled: bool = True) -> None:
        """
        为当前群聊设置推送任务
        :param script_path: 脚本路径（如 "scripts/weather.py"）
        :param cron_expr: 定时表达式（可选，如 "0 8 * * *" 表示每天8点）
        :param session_id: 会话ID（可选，默认使用事件的会话ID）
        """

        # 验证cron表达式格式
        if cron_expr != "-1" and not self._is_valid_cron(cron_expr):
            logger.error(f"无效的cron表达式: {cron_expr}")
            raise ValueError(f"无效的cron表达式: {cron_expr}")

        # 写入配置
        async with aiofiles.open(self.storage_group_config, "r+", encoding="utf-8") as f:
            # 读取文件内容
            content = await f.read()
            # 解析为 JSON 对象
            group_settings = json.loads(content) if content else {}
            # 更新群组配置
            if session_id not in group_settings:
                group_settings[session_id] = {}
            
            # 在群组配置中添加/修改推送任务
            for task in group_settings[session_id].get("push_tasks", []):
                if task["script_path"] == script_path:
                    if cron_expr != "-1":
                        # 修改已存在任务
                        task.update({"cron_expr": cron_expr,})
                    # 修改已存在任务
                    task.update({
                        "enabled": enabled,
                    })
                    logger.info(f"已修改脚本路径为 {script_path} 的推送任务，cron表达式为 {cron_expr}，状态为 {'开启' if enabled else '关闭'}")
            else:
                logger.info(f"未找到脚本路径为 {script_path} 的推送任务，添加新任务")
                # 添加新任务
                group_settings[session_id]["push_tasks"] = group_settings[session_id].get("push_tasks", []) + [
                    {
                        "script_path": script_path,
                        "cron_expr": cron_expr if cron_expr != "-1" else "0 8 * * *",
                        "enabled": enabled,
                    }
                ]


            # 写入文件
            logger.info(f"已添加脚本路径为 {script_path} 的推送任务，cron表达式为 {cron_expr}，状态为 {'开启' if enabled else '关闭'}")
            await f.seek(0)
            await f.write(json.dumps(group_settings, ensure_ascii=False, indent=4))
            await f.truncate()
        
    async def remove_push_task(self, session_id: str, script_path: str) -> None:
        """
        为当前群聊移除推送任务
        :param script_path: 脚本路径（如 "scripts/weather.py"）
        :param session_id: 会话ID（可选，默认使用事件的会话ID）
        """
        # 写入配置
        async with aiofiles.open(self.storage_group_config, "r+", encoding="utf-8") as f:
            # 读取文件内容
            content = await f.read()
            # 解析为 JSON 对象
            group_settings = json.loads(content) if content else {}
            # 更新群组配置
            if session_id not in group_settings:
                group_settings[session_id] = {}
            
            # 在群组配置中移除推送任务
            for task in group_settings[session_id].get("push_tasks", []):
                if task["script_path"] == script_path:
                    # 移除任务
                    group_settings[session_id]["push_tasks"].remove(task)
                    break
            else:
                # 未找到任务
                logger.error(f"未找到脚本路径为 {script_path} 的推送任务")
                return




