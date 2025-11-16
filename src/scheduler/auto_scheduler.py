"""
自动调度器模块
负责定时任务
两种模式：
一种是每日固定时候执行
另一种是固定时间间隔执行
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
        
    async def start_scheduler(self):
        """启动自动调度器"""

        await asyncio.sleep(1)  # 等待1秒，确保配置加载完成


        logger.info(
            f"启动定时任务调度器"
        )

        self.scheduler_task = asyncio.create_task(self._scheduler_loop())

    async def stop_scheduler(self):
        """停止自动调度器"""
        if self.scheduler_task:
            self.scheduler_task.cancel()
            logger.info("定时任务调度器已停止")

    async def restart_scheduler(self):
        """重启定时任务调度器"""
        await self.stop_scheduler()
        await self.start_scheduler()

    async def _scheduler_loop(self):
        """定时任务循环"""
        while True:

            try:
                self.mode = self.config_manager.get_mode()
                now = datetime.now()

                
                if self.mode == "daily":
                    target_time = datetime.strptime(
                        self.config_manager.get_push_time(),
                        "%H:%M"
                    ).replace(year=now.year, month=now.month, day=now.day)

                elif self.mode == "interval":
                    target_time = now + timedelta(
                        minutes=self.config_manager.get_push_interval()
                    )

                else:
                    logger.error(f"未知的调度模式：{self.mode}, 已切换为默认模式：daily")
                    self.mode = "daily"
                    continue

                # 若今天目标时间已过，设置为下一个周期
                if now > target_time:
                    if self.mode == "daily":
                        target_time += timedelta(days=1)
                    elif self.mode == "interval":
                        target_time += timedelta(
                            minutes=self.config_manager.get_push_interval()
                        )

                wait_time = (target_time - now).total_seconds()
                logger.info(
                    f"推送任务将在 {wait_time:.2f} 秒后，直到 {target_time.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                await asyncio.sleep(wait_time)

                # 开始推送
                await self._push_notices()
            
            except Exception as e:
                logger.error(f"推送通知时出错: {str(e)}")
                continue

    async def _push_notices(self):
        """推送通知 - 通知所有群聊"""
        try:
            logger.info("开始推送通知")

            enabled_groups = self.config_manager.get_enabled_groups()
            if not enabled_groups:
                logger.warning("没有启用的群聊，跳过推送")
                return
            
            logger.info(f"将通知 {len(enabled_groups)} 个群聊: {enabled_groups}")

            # 1.从url获取内容
            html_content = await self.html_render_func()
            if not html_content:
                logger.error("获取HTML内容失败，跳过推送")
                return
            
            # 2.解析，写入本地
            notices = self.NoticeDataHandler.parse_notices(html_content)
            if not notices:
                logger.error("解析通知失败，跳过推送")
                return
            new_notices = self.NoticeDataHandler.save_notices(notices)
            if not new_notices:
                logger.info("没有新的通知，跳过推送")
                return
            
            # 3.生成新增通知的报告
            image_url = await self.ReportGenerator.generate_report(new_notices)
            if not image_url:
                logger.error("生成报告失败，跳过推送")
                return
            

            for group_id in enabled_groups:
                try:
                    bot_instance = self.bot_manager.get_bot_instance()
                    if not bot_instance:
                        logger.error("获取机器人实例失败，跳过推送")
                        return
                    

                    await bot_instance.api.call_action(
                        action="send_group_msg",
                        group_id=group_id,
                        message=[
                            {"type": "image", "data": {"url": image_url}}
                            ]
                        )

                except Exception as e:
                    logger.error(f"发送通知到群聊 {group_id} 失败: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"推送通知时出错: {str(e)}")
            return



    # 接口
    def set_mode(self, mode: str):
        """
        设置调度模式
        参数：
        mode (str): 调度模式，可选值为 "daily" 和 "interval"
        """
        self.mode = mode
        logger.info(f"设置调度模式为：{mode}")