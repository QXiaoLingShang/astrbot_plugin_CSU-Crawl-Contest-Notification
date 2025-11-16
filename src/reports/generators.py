"""
报告生成器模块
"""

import asyncio
from datetime import datetime, timedelta
from astrbot.api import logger
from typing import Dict, Optional
from .templates import HTMLTemplates
import csv
from pathlib import Path
from typing import List

class ReportGenerator:
    """报告生成器"""


    def __init__(self, config_manager):
        self.config_manager = config_manager

    
    async def generate_image_report(
        self, html_render_func, page: Optional[int] = None, list_len: Optional[int] = None
    ) -> Optional[str]:
        """生成活动分析报告图片"""
        try:
            if page is None or list_len is None:
                page = 1
                list_len = 15
                logger.warning(f"page和list_len参数未指定，使用默认值 page={page}, list_len={list_len}")
            
            # 准备渲染数据
            render_payload = await self._prepare_render_data(page, list_len)

            # 使用AstrBot内置的HTML渲染服务（直接传递模板和数据）
            # 使用兼容的图片生成选项（基于NetworkRenderStrategy的默认设置）
            image_options = {
                "full_page": True,
                "type": "jpeg",  # 使用默认的jpeg格式提高兼容性
                "quality": 95,  # 设置合理的质量
            }
            image_url = await html_render_func(
                HTMLTemplates.get_image_template(),
                render_payload,
                True,  # return_url=True，返回URL而不是下载文件
                image_options,
            )

            logger.info(f"生成活动分析报告图片成功，URL: {image_url}")
            return image_url
        
        except Exception as e:
            logger.error(f"生成活动分析报告图片失败: {str(e)}", exc_info=True)
            return None
        
    
    

    async def _prepare_render_data(self, page, list_len) -> Dict:
        """
        准备渲染数据
        参数：
        page: 页码（从1开始）
        list_len: 列表长度（最大不超过15）
        """
        

        # 初始化通知列表HTML
        notices_html = ""
        notice_file = Path(self.config_manager.get_storage_file())
        
        try:
            # 读取CSV文件内容
            with open(notice_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)  # 使用标题行作为键
                notices = list(reader)  # 转换为列表以便倒序排序
            
            # 按时间倒序排列（最新的在前）
            notices.sort(key=lambda x: x['时间'], reverse=True)
            
            # 构建通知列表HTML
            for i, notice in enumerate(notices, 1):
                if i < (page - 1) * list_len + 1 or i >= page * list_len + 1:
                    continue  # 跳过不在范围内的索引
                
                # 格式化时间显示（可根据需要调整）
                formatted_date = notice['时间']
                
                # 拼接单个通知的HTML
                notices_html += f"""
                <div class="notice-item">
                    <div class="notice-header">
                        <!-- 序号：左对齐 -->
                        <span class="notice-number">{i}</span>
                        <!-- 标题：中间填充，左对齐 -->
                        <div class="notice-title-wrapper">
                            <a href="{notice['链接']}" target="_blank">{notice['标题']}</a>
                        </div>
                        <!-- 日期：右对齐 -->
                        <span class="notice-date">{formatted_date}</span>
                    </div>
                </div>
                """

    
        except Exception as e:
            # 处理文件读取错误（如文件不存在、格式错误等）
            notices_html = f"""
            <div class="error-message">
                无法加载通知数据：{str(e)}
            </div>
            """
        
        # 返回渲染所需的完整数据字典
        return {
            "report_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "notice_count": len(notices) if 'notices' in locals() else 0,
            "page": page,
            "list_len": list_len,
            "latest_update": notices[0]['时间'] if 'notices' in locals() and notices else "无数据",
            "notices_html": notices_html
        }
    
    async def _prepare_render_data_new(self, new_notices: List[Dict]) -> Optional[Dict]:
        """
        准备新通知报告图片
        参数：
        new_notices: 新通知列表（字典格式）
        """
        # 检查是否有新通知
        if not new_notices:
            logger.info("没有新通知可生成报告")
            return None
        
        # 初始化通知列表HTML
        notices_html = ""
        notice_file = Path(self.config_manager.get_storage_file())
        
        try:
            # 读取CSV文件内容
            with open(notice_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)  # 使用标题行作为键
                notices = list(reader)  # 转换为列表以便倒序排序
            
            # 按时间倒序排列（最新的在前）
            notices.sort(key=lambda x: x['时间'], reverse=True)
            
            # 构建通知列表HTML
            i = 1
            for notice in new_notices:
                # 格式化时间显示（可根据需要调整）
                formatted_date = notice['时间']
                
                # 拼接单个通知的HTML
                notices_html += f"""
                <div class="notice-item">
                    <div class="notice-header">
                        <!-- 序号：左对齐 -->
                        <span class="notice-number">{i}</span>
                        <!-- 标题：中间填充，左对齐 -->
                        <div class="notice-title-wrapper">
                            <a href="{notice['链接']}" target="_blank">{notice['标题']}</a>
                        </div>
                        <!-- 日期：右对齐 -->
                        <span class="notice-date">{formatted_date}</span>
                    </div>
                </div>
                """
                i += 1

        except Exception as e:
            # 处理文件读取错误（如文件不存在、格式错误等）
            notices_html = f"""
            <div class="error-message">
                无法加载通知数据：{str(e)}
            </div>
            """
            return None
        
        # 返回渲染所需的完整数据字典
        return {
            "report_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "notices_html": notices_html
        }


    async def generate_new_image_report(
        self, html_render_func, new_notices: List[Dict]
    ) -> Optional[str]:
        """
        准备新通知报告图片
        参数：
        html_render_func: 异步HTML渲染函数
        new_notices: 新通知列表（字典格式）
        """

        # 检查是否有新通知
        if not new_notices:
            logger.info("没有新通知可生成报告")
            return None
        
        try:
            # 准备渲染数据
            render_payload = await self._prepare_render_data_new(new_notices)
            if not render_payload:
                logger.error("无法准备渲染数据")
                return None

            # 使用AstrBot内置的HTML渲染服务（直接传递模板和数据）
            # 使用兼容的图片生成选项（基于NetworkRenderStrategy的默认设置）
            image_options = {
                "full_page": True,
                "type": "jpeg",  # 使用默认的jpeg格式提高兼容性
                "quality": 95,  # 设置合理的质量
            }
            image_url = await html_render_func(
                HTMLTemplates.get_new_image_template(),
                render_payload,
                True,  # return_url=True，返回URL而不是下载文件
                image_options,
            )

            logger.info(f"生成新增通知报告图片成功，URL: {image_url}")
            return image_url
        
        except Exception as e:
            logger.error(f"生成新增通知报告图片失败: {str(e)}", exc_info=True)
            return None