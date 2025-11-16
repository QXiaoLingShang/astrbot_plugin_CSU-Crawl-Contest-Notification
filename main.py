from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api import AstrBotConfig
from .src.core import BotManager, ConfigManager, NoticeDataHandler
from .src.reports import ReportGenerator
from .src.scheduler import AutoScheduler



@register("helloworld", "Xiao_LingShang", "一个简单的 Hello World 插件", "0.0.1")
class MyPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        logger.info(self.config)


        # 初始化配置管理器
        self.config_manager = ConfigManager(self.config)        
        logger.info(f"""
                    插件初始化完成 - 目标URL: {self.config_manager.get_url()}, 
                     机器人的qqID: {self.config_manager.get_bot_qq_id()},
                     基础URL: {self.config_manager.get_base_url()}, 
                     推送时间: {self.config_manager.get_push_time()}, 
                     本地存储路径: {self.config_manager.get_storage_file()}"
                    """
                     )

        # 初始化数据处理工具
        self.data_handler = NoticeDataHandler(
            base_url=self.config_manager.get_base_url(),
            storage_path=self.config_manager.get_storage_file()
        )

        # 初始化报告生成器
        self.report_generator = ReportGenerator(self.config_manager)

        # 
        self.bot_manager = BotManager(self.config_manager)
        self.bot_manager.set_context(context)
        self.auto_scheduler = AutoScheduler(
            config_manager=self.config_manager,
            NoticeDataHandler=self.data_handler,
            ReportGenerator=self.report_generator,
            html_render_func=self.html_render,
            bot_manager=self.bot_manager,
        )


    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        # 启动自动调度器
        await self.auto_scheduler.start_scheduler()
        await self.bot_manager.initialize_from_config()


        # 预处理
        # 事先爬取https://bksy.csu.edu.cn/tztg/cxycyjybgs/xx.htm里所有通知，xx为1~18
        # 若本地存储的数量过少，爬取所有通知
        if len(self.data_handler._get_existing_links()) < 250:
            logger.info("本地存储的通知数量过少，开始爬取所有通知")
            for page in range(1, 19):
                test_content = await self.data_handler.fetch_url_content(f"https://bksy.csu.edu.cn/tztg/cxycyjybgs/{page}.htm")
                # 写入
                notices = self.data_handler.parse_notices(test_content)
                new_count = self.data_handler.save_notices(notices)
                logger.info(f"写入了{new_count}条新通知")



    # 注册指令的装饰器。
    # @filter.command("helloworld")
    # async def helloworld(self, event: AstrMessageEvent):
    #     """这是一个 hello world 指令""" # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
    #     user_name = event.get_sender_name()
    #     message_str = event.message_str # 用户发的纯文本消息字符串
    #     message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
    #     logger.info(message_chain)
    #     yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!") # 发送一条纯文本消息



    # 配置
    @filter.command("CSU通知配置", alias={"csu通知配置", "Csu通知配置"})
    async def config(self, event: AstrMessageEvent):
        # 手动计算距离下次执行时间
        """查看配置"""
        configText = f"""
        配置信息：
        - 目标URL: {self.config_manager.get_url()}
        - 下次自动更新时间: {self.auto_scheduler.get_next_execution_time()}
        """
        yield event.plain_result(configText)


    @filter.command("CSU通知查找", alias={"csu通知查找", "Csu通知查找"})
    async def restart(self, event: AstrMessageEvent, page: int = 1, list_len: int = 10):
        """查找本地缓存的通知，格式：CSU通知查找 [页码] [每页数量]
        参数：
        - page: 要查找的页码，默认第1页
        - list_len: 每页显示的通知数量，默认10条
        """
        try:
            image_url = await self.report_generator.generate_image_report(self.html_render, page, list_len)
            if image_url:
                yield event.image_result(image_url)
            else:
                yield event.plain_result("❌ 报告图片生成失败")

        except Exception as e:
            logger.error(f"查找通知时出错: {str(e)}")
            yield event.plain_result("❌ 查找通知时出错，请稍后重试")

    @filter.command("CSU通知更新", alias={"csu通知更新", "Csu通知更新"})
    async def update(self, event: AstrMessageEvent):
        """更新本地存储的通知"""
        try:
            # 1. 从URL获取内容
            html_content = await self.data_handler.fetch_url_content(self.config_manager.get_url())
            if not html_content:
                yield event.plain_result("❌ 无法获取URL内容，请检查链接是否有效")
                return

            # 2. 解析并保存通知
            notices = self.data_handler.parse_notices(html_content)
            new_notices = self.data_handler.save_notices(notices)
            if len(new_notices) > 0:
                yield event.plain_result(f"✅ 已保存 {len(new_notices)} 条新通知到本地")    

                # 3. 生成new_notices的报告图片
                image_url = await self.report_generator.generate_new_image_report(self.html_render, new_notices)

                if image_url:
                    yield event.image_result(image_url)
                    # 合成通知链接
                    notice_link = ""
                    for notice in new_notices:
                        notice_link += notice["标题"] + ": " + notice["链接"] + "\n"

                    yield event.plain_result(f"新增通知链接：\n{notice_link}")
                else:
                    yield event.plain_result("❌ 报告图片生成失败")
            
            else:
                yield event.plain_result("❌ 没有新通知")

        except Exception as e:
            logger.error(f"更新通知时出错: {str(e)}")
            yield event.plain_result("❌ 更新通知时出错，请稍后重试")


    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
        # 关闭自动调度器
        await self.auto_scheduler.stop_scheduler()