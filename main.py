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


        # 预处理
        # 事先爬取https://bksy.csu.edu.cn/tztg/cxycyjybgs/xx.htm里所有通知，xx为1~18
        # 若本地存储的数量过少，爬取所有通知
        if len(self.data_handler._get_existing_links()) < 250:
            logger.info("本地存储的通知数量过少，开始爬取所有通知")
            for page in range(1, 19):
                test_content = self.data_handler.fetch_url_content(f"https://bksy.csu.edu.cn/tztg/cxycyjybgs/{page}.htm")
                # 写入
                notices = self.data_handler.parse_notices(test_content)
                new_count = self.data_handler.save_notices(notices)
                logger.info(f"写入了{new_count}条新通知")


    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""





    # 注册指令的装饰器。
    @filter.command("helloworld")
    async def helloworld(self, event: AstrMessageEvent):
        """这是一个 hello world 指令""" # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        user_name = event.get_sender_name()
        message_str = event.message_str # 用户发的纯文本消息字符串
        message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        logger.info(message_chain)
        yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!") # 发送一条纯文本消息



    # 配置
    @filter.command("config")
    async def config(self, event: AstrMessageEvent):
        """查看配置"""
        configText = f"""
        配置信息：
        - 目标URL: {self.config_manager.get_url()}
        - 推送时间: {self.config_manager.get_push_time()}
        - 本地存储路径: {self.config_manager.get_storage_file()}
        """
        yield event.plain_result(configText)






    # 测试指令：爬取通知并发送前10条
    @filter.command("test")
    async def test_command(self, event: AstrMessageEvent, page: int = 1, list_len: int = 10):
        """测试指令：爬取通知并发送前10条"""
        try:
            # 1. 从URL获取内容
            yield event.plain_result(f"开始从配置URL第{page}页爬取通知...")
            html_content = self.data_handler.fetch_url_content(self.config_manager.get_url())
            if not html_content:
                yield event.plain_result("❌ 无法获取URL内容，请检查链接是否有效")
                return

            # 2. 解析并保存通知
            notices = self.data_handler.parse_notices(html_content)
            new_notices = self.data_handler.save_notices(notices, ret_mode="list")
            if isinstance(new_notices, list) and len(new_notices) > 0:
                yield event.plain_result(f"✅ 已保存 {len(new_notices)} 条新通知到本地")    

                # 3. 生成new_notices的报告图片
                image_url = await self.report_generator.generate_new_image_report(self.html_render, new_notices)
                if image_url:
                    yield event.image_result(image_url)
                else:
                    yield event.plain_result("❌ 报告图片生成失败")



            # # 3. 读取本地第page页前list_len条通知并发送
            # yield event.plain_result(f"读取本地第{page}页前{list_len}条通知...")
            # top_notices = self.data_handler.read_notices(list_len, page)
            # if not top_notices:
            #     yield event.plain_result(f"⚠️ 本地第{page}页暂无通知数据")
            #     return

            # # 格式化消息
            # message = f"本地存储的第{page}页前{list_len}条通知：\n\n"
            # for i, notice in enumerate(top_notices, 1):
            #     message += f"{i}. 时间：{notice['时间']}\n"
            #     message += f"   标题：{notice['标题']}\n"
            #     message += f"   链接：{notice['链接']}\n\n"
            
            # yield event.plain_result(message.strip())

            # 生成报告
            yield event.plain_result("生成报告...")
            image_url = await self.report_generator.generate_image_report(self.html_render, page, list_len)
            if image_url:
                yield event.image_result(image_url)
            else:
                yield event.plain_result("❌ 报告图片生成失败")

        except Exception as e:
            logger.error(f"测试指令执行失败: {str(e)}")
            yield event.plain_result(f"❌ 操作失败：{str(e)}")


    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
