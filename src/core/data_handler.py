"""
数据处理模块
对数据进行爬取、处理、保存等等操作
"""


import os
import csv
# import requests 这种非异步的方式，问题是会阻塞事件循环
import aiohttp  # 异步HTTP客户端
from astrbot.api import logger
from bs4 import BeautifulSoup
from datetime import datetime   
from ..core import ConfigManager

class NoticeDataHandler:
    """中南大学通知数据处理工具类"""
    
    def __init__(self, config: ConfigManager):
        self.storage_path = config.get_storage_root() + "csu_innovation_notices.csv"   # 本地存储文件路径
        self.base_url = config.get_base_url()                           # 用于补全相对链接的基础URL
        self._init_storage()                                            # 初始化存储目录

    def _init_storage(self):
        """初始化存储目录（如果不存在则创建）"""
        dir_path = os.path.dirname(self.storage_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"创建存储目录: {dir_path}")

    async def fetch_url_content(self, target_url: str) -> str:
        """从目标URL获取页面内容"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(target_url, headers=headers, timeout=10) as response:
                    response.raise_for_status()  # 触发HTTP错误
                    # response.encoding = "UTF-8"
                    logger.info(f"成功获取URL内容: {target_url}")
                    return await response.text()
        except Exception as e:
            logger.error(f"获取URL内容失败: {str(e)}")
            return ""

    def parse_notices(self, html_content: str) -> list:
        """解析HTML内容，提取通知数据（时间、标题、链接）"""
        if not html_content:
            logger.warning("HTML内容为空，无法解析")
            return []

        soup = BeautifulSoup(html_content, "html.parser")
        right_list = soup.find("ul", class_="right-list")
        if not right_list:
            logger.warning("未找到通知列表容器（ul.right-list）")
            return []

        notices = []
        for item in right_list.find_all("li"):
            a_tag = item.find("a")
            span_tag = item.find("span")
            if not (a_tag and span_tag):
                continue  # 跳过不完整的条目

            # 提取并处理数据
            title = a_tag.get_text(strip=True)
            link = a_tag.get("href", "")
            # 补全相对链接（如 ../xxx → https://bksy.csu.edu.cn/xxx）
            if str(link).startswith("../"):
                link = str(link).replace("../", "")
                link = f"{self.base_url}/{link}"
            time = span_tag.get_text(strip=True).strip("[]")

            notices.append({
                "时间": time,
                "标题": title,
                "链接": link
            })

        logger.info(f"成功解析 {len(notices)} 条通知数据")
        return notices

    def save_notices(self, new_notices: list) -> list[dict]:
        """
        写入通知到本地
        返回新增通知列表
        """
        if not new_notices:
            return []

        # 获取已存在的链接（用于去重）
        existing_links = self._get_existing_links()
        # 筛选未存储过的通知
        filtered_notices = [
            notice for notice in new_notices
            if notice["链接"] not in existing_links
        ]
        if not filtered_notices:
            logger.info("没有新通知需要保存")
            return []



        # 追加写入CSV
        with open(self.storage_path, "a", encoding="UTF-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["时间", "标题", "链接"])
            # 如果文件为空，先写表头
            if not os.path.exists(self.storage_path) or os.path.getsize(self.storage_path) == 0:
                writer.writeheader()
            # 写入新通知
            writer.writerows(filtered_notices)

        logger.info(f"已保存 {len(filtered_notices)} 条新通知到 {self.storage_path}")

        # 对Csv文件进行排序
        self.sort_notices_by_time()
        
        return filtered_notices

    def _get_existing_links(self) -> set:
        """获取本地已存储的所有通知链接（用于去重）"""
        if not os.path.exists(self.storage_path) or os.path.getsize(self.storage_path) == 0:
            return set()

        try:
            with open(self.storage_path, "r", encoding="UTF-8") as f:
                reader = csv.DictReader(f)
                return {row["链接"] for row in reader}
        except Exception as e:
            logger.error(f"读取已存储链接失败: {str(e)}")
            return set()

    # 重构本地的csv文件， 按时间排序
    def sort_notices_by_time(self):
        """根据时间字段对本地CSV文件进行排序"""
        if not os.path.exists(self.storage_path) or os.path.getsize(self.storage_path) == 0:
            logger.info("本地存储文件为空或不存在，无需排序")
            return
        
        try:
            # 读取所有行
            with open(self.storage_path, "r", encoding="UTF-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            # 按时间字段排序，新的在前面
            rows.sort(key=lambda x: datetime.strptime(x["时间"], "%Y-%m-%d"), reverse=True)
            
            # 写回文件
            with open(self.storage_path, "w", encoding="UTF-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["时间", "标题", "链接"])
                writer.writeheader()
                writer.writerows(rows)
            

            logger.info(f"已按时间排序 {len(rows)} 条通知")
        except Exception as e:
            logger.error(f"排序本地通知失败: {str(e)}")

    # 对外接口
    def read_top_n(self, n: int) -> list:
        """读取本地存储的前N条通知"""
        if not os.path.exists(self.storage_path) or os.path.getsize(self.storage_path) == 0:
            logger.info("本地存储文件为空或不存在")
            return []

        try:
            with open(self.storage_path, "r", encoding="UTF-8") as f:
                reader = csv.DictReader(f)
                # 取前N条并转为列表
                top_notices = list(reader)[:n]
                logger.info(f"成功读取前 {len(top_notices)} 条通知")
                return top_notices
        except Exception as e:
            logger.error(f"读取本地通知失败: {str(e)}")
            return []
    
    def read_notices(self, n: int, page: int) -> list:
        """读取本地存储的第page页前n条通知"""
        if not os.path.exists(self.storage_path) or os.path.getsize(self.storage_path) == 0:
            logger.info("本地存储文件为空或不存在")
            return []

        try:
            with open(self.storage_path, "r", encoding="UTF-8") as f:
                reader = csv.DictReader(f)
                # 计算跳过的条数
                skip = (page - 1) * n
                # 取第page页前n条并转为列表
                notices = list(reader)[skip:skip+n]
                logger.info(f"成功读取第{page}页前 {len(notices)} 条通知")
                return notices
        except Exception as e:
            logger.error(f"读取本地通知失败: {str(e)}")
            return []
