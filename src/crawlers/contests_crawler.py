"""
爬取各种编程比赛通知
具体平台：atcoder, lougu, cf, nowcoder, leetcode
"""


# 标准库导入
import json
import os
import time
from typing import Optional, List
from datetime import datetime, timezone
from html import unescape

# 第三方库导入
import aiohttp
import aiofiles
from bs4 import BeautifulSoup

# 本地模块导入
from astrbot.api import logger
from .Contest import Contest
from ..core import ConfigManager


class ContestCrawler:
    """
    爬取各种编程比赛通知的基类
    """

    def __init__(self, config: ConfigManager):
        self.config = config
        self.storage_path = os.path.join(
            self.config.get_storage_root(), "json_innovation_contests.json"
        )
        self.storage_path_atcoder = os.path.join(
            self.config.get_storage_root(), "json_innovation_contests_atcoder.json"
        )
        self._init_storage()

    def _init_storage(self):
        """初始化存储目录（如果不存在则创建）"""
        dir_path = os.path.dirname(self.storage_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"创建存储目录: {dir_path}")

    ###### 工具函数 - 获取各个平台的比赛 ######

    async def _fetch_cf_contest(self) -> list[Contest]:
        """
        获取cf比赛
        """
        os.environ['NO_PROXY'] = 'codeforces.com'
        url = 'https://codeforces.com/api/contest.list'
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0'
        headers = {'User-Agent': user_agent}
        res = []
        n = 100     # 筛选前n个比赛

        # 开始爬取
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout = self.config.get_timeout()) as resp:

                    if resp.status != 200:
                        logger.error(f"Codeforces API返回状态码 {resp.status}")
                        return res

                    # 解析
                    resp_text = await resp.text()
                    url_get_par = json.loads(resp_text)

                    if url_get_par['status'] != 'OK':
                        logger.error(f"Codeforces API返回状态码 {url_get_par['status']}")
                        return res
                    
                    contests = url_get_par['result'][:n]

                    for info in contests:

                        if (info['phase'] != 'BEFORE'):
                            continue

                        
                        contest_id = info.get('id')
                        name = info.get('name')
                        start_time = info.get('startTimeSeconds')
                        duration = info.get('durationSeconds')


                        # 关键信息不全则跳过
                        if not all([contest_id, name, start_time, duration]):
                            continue

                        end_time = start_time + duration

                        res.append(Contest(oj='cf', name=name, stime=start_time, etime=end_time, dtime=duration, link=f"https://codeforces.com/contests/{contest_id}"))
                    logger.info(f"爬取code force比赛完成，共{len(res)}个比赛")
                    return res
        except Exception as e:
            logger.error(f"Codeforces API获取比赛列表失败: {str(e)}")
            return res
 

    async def _fetch_lougu_contest(self) -> list[Contest]:
        """
        获取lougu比赛
        """
        url = 'https://www.luogu.com.cn/contest/list?page=1&_contentOnly=1'
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0'
        headers = {'User-Agent': user_agent}
        res = []
        currentTime = time.time()

        # 开始爬取
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout = self.config.get_timeout()) as resp:

                    if resp.status != 200:
                        logger.error(f"Luogu API返回状态码 {resp.status}")
                        return res

                    # 解析
                    resp_text = await resp.text()
                    url_get_par = json.loads(resp_text)
                    contests = url_get_par['currentData']['contests']['result']

                    for info in contests:

                        if (currentTime > info.get('startTime')):
                            continue
                            
                        
                        name = info.get('name')
                        start_time = info.get('startTime')
                        end_time = info.get('endTime')
                        dtime = end_time - start_time
                        link = f'https://www.luogu.com.cn/contest/{info["id"]}'

                        # 关键信息不全则跳过
                        if not all([name, start_time, end_time, link]):
                            continue


                        res.append(Contest(oj='lougu', name=name, stime=start_time, etime=end_time, dtime=dtime, link=link))
                    logger.info(f"爬取luogu比赛完成，共{len(res)}个比赛")
                    return res
        except Exception as e:
            logger.error(f"Luogu API获取比赛列表失败: {str(e)}")
            return res
        

    async def _fetch_atcoder_contest(self) -> list[Contest]:
        """
        获取atcoder比赛
        """
        url = 'https://atcoder.jp/contests/'
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0'
        headers = {'User-Agent': user_agent}
        res = []
        currentTime = datetime.now()

        # 这个比赛反爬虫比较严格，需要设置爬取间隔，一天爬取一次，通过读取本地文件判断是否需要刷新
        try:
            async with aiofiles.open(self.storage_path_atcoder, 'r', encoding='utf-8') as f:
                atcoder_contests = json.loads(await f.read())
                last_refresh_time = datetime.fromtimestamp(atcoder_contests['time'])

                if (currentTime - last_refresh_time).days < 1:
                    logger.info(f"Atcoder距离上一次刷新时间{currentTime - last_refresh_time}，小于1天，不进行刷新")
                    return res
        except FileNotFoundError:
            logger.warning(f"Atcoder比赛文件{self.storage_path_atcoder}不存在，正在正常爬取进行更新")



        # 开始爬取
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout = self.config.get_timeout()) as resp:

                    if resp.status != 200:
                        logger.error(f"Atcoder API返回状态码 {resp.status}")
                        return res

                    # 解析
                    resp_text = await resp.text()
                    soup = BeautifulSoup(resp_text, 'html.parser')


                    # 获取即将到来的比赛表格
                    contest_table = soup.find('div', id='contest-table-upcoming')
                    if not contest_table:
                        logger.warning("未找到AtCoder比赛表格")
                        return res

                    check = True  # 用于跳过表头行
                    for row in contest_table.find_all('tr'):
                        if check:
                            check = False
                            continue
                            
                        contest = Contest(oj='atcoder')
                        cells = row.find_all('td')
                        
                        for i, cell in enumerate(cells):
                            if i == 0:
                                # 处理开始时间
                                time_tag = cell.find('time')
                                if not time_tag:
                                    continue
                                    
                                datetime_str = time_tag.text
                                # 解析带时区的时间字符串
                                dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S%z")
                                # 转换为UTC时间
                                dt_utc = dt.astimezone(timezone.utc)
                                # 转换为时间戳（UTC+8）
                                timestamp = int(dt_utc.timestamp())
                                contest.stime = timestamp  # 转为东八区时间戳
                                
                            elif i == 1:
                                # 处理比赛链接和名称
                                a_tag = cell.find('a')
                                if not a_tag:
                                    continue
                                
                                contest.link = 'https://atcoder.jp' + a_tag.get('href', '') # type: ignore
                                contest.name = a_tag.text.strip()
                                
                            elif i == 2:
                                # 处理比赛时长
                                time_text = cell.text.strip()
                                nums = [int(num) for num in time_text.split(':') if num.isdigit()]
                                if len(nums) >= 2:
                                    contest.dtime = nums[0] * 3600 + nums[1] * 60
                                    contest.etime = contest.stime + contest.dtime
                        
                        res.append(contest)

                    # 按开始时间排序
                    res.sort(key=lambda x: x.stime)
                    logger.info(f"爬取atcoder比赛完成，共{len(res)}个比赛")
                    return res
        except Exception as e:
            logger.error(f"Atcoder API获取比赛列表失败: {str(e)}")
            return res


    async def _fetch_nowcoder_contest(self) -> list[Contest]:
        """
        获取nowcoder比赛
        """
        url = 'https://ac.nowcoder.com/acm/contest/vip-index?topCategoryFilter=13'
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0'
        headers = {'User-Agent': user_agent}
        res = []
        currentTime = time.time()

        # 开始爬取
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout = self.config.get_timeout()) as resp:

                    if resp.status != 200:
                        logger.error(f"Atcoder API返回状态码 {resp.status}")
                        return res

        #           # 解析
                    resp_text = await resp.text()
                    soup = BeautifulSoup(resp_text, 'html.parser')


                    # 获取即将到来的比赛表格
                    contest_container = soup.find('div', class_='platform-mod js-current')
                    if not contest_container:
                        logger.warning("未找到nowcoder比赛表格")
                        return res

                    # 解析每个比赛项
                    for item in contest_container.find_all('div', class_='platform-item js-item'):
                        data_json = item.get('data-json')
                        if not data_json:
                            continue
                            
                        try:
                            # 解析JSON数据
                            info = json.loads(unescape(str(data_json)))
                            contest = Contest(oj='nowcoder')
                            contest.dtime = int(info.get('contestDuration', 0) / 1000)
                            contest.stime = int(info.get('contestStartTime', 0) / 1000)
                            contest.etime = int(info.get('contestEndTime', 0) / 1000)
                            contest.name = info.get('contestName', '未知比赛')
                            contest_id = info.get('contestId')
                            contest.link = f'https://ac.nowcoder.com/acm/contest/{contest_id}' if contest_id else ''
                            
                            res.append(contest)
                        except (json.JSONDecodeError, KeyError, ValueError) as e:
                            logger.warning(f"解析NowCoder比赛数据失败: {str(e)}")
                            continue

                    # 按开始时间排序
                    res.sort(key=lambda x: x.stime)

                    logger.info(f"爬取nowcoder比赛完成，共{len(res)}个比赛")
                    return res
        except Exception as e:
            logger.error(f"NowCoder API获取比赛列表失败: {str(e)}")
            return res


    async def _fetch_leetcode_contest(self) -> list[Contest]:
        """
        获取LeetCode比赛信息
        """
        url = 'https://leetcode.com/graphql'
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0'
        headers = {
            'Referer': 'https://leetcode.cn/',
            'Content-Type': 'application/json',
            'User-Agent': user_agent
        }
        res = []

        # GraphQL查询数据
        data = {
            'operationName': None,
            'variables': {},
            'query': '''
            {
                allContests {
                    title
                    titleSlug
                    startTime
                    duration
                    isVirtual
                }
            }
            '''
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=json.dumps(data), timeout=self.config.get_timeout()) as resp:
                    if resp.status != 200:
                        logger.error(f"LeetCode API返回状态码 {resp.status}")
                        return res

                    resp_text = await resp.text()
                    try:
                        resp_json = json.loads(resp_text)
                        contests = resp_json.get("data", {}).get("allContests", [])
                    except json.JSONDecodeError as e:
                        logger.error(f"解析LeetCode响应失败: {str(e)}")
                        return res

                    current_time = time.time()
                    for info in contests:
                        # 过滤虚拟比赛和已结束比赛
                        if info.get("isVirtual", False):
                            continue
                            
                        end_time = info.get("startTime", 0) + info.get("duration", 0)
                        if end_time < current_time:
                            continue

                        # 构造比赛信息
                        contest = Contest(oj='leetcode')
                        contest.dtime = info.get("duration", 0)
                        contest.stime = info.get("startTime", 0)
                        contest.etime = contest.stime + contest.dtime
                        contest.name = info.get("title", "未知比赛")
                        title_slug = info.get("titleSlug")
                        contest.link = f'https://leetcode.cn/contest/{title_slug}' if title_slug else ''
                        
                        res.append(contest)

                    # 按开始时间排序
                    res.sort(key=lambda x: x.stime)

                    logger.info(f"爬取leetcode比赛完成，共{len(res)}个比赛")
                    return res

        except Exception as e:
            logger.error(f"LeetCode API获取比赛列表失败: {str(e)}")
            return res
        

    async def _save_contest(self, contests: list[Contest], path: str):
        """
        保存比赛信息到本地文件
        """
        if (contests != []):
            atcoder_contests = {
                "time": int(datetime.now().timestamp()),
                "data": [contest.__dict__ for contest in contests]
            }
            async with aiofiles.open(path, mode='w', encoding='utf-8') as f:
                await f.write(json.dumps(atcoder_contests, ensure_ascii=False, indent=4))

    async def _read_contest(self, path: str) -> list[Contest]:
        """
        从本地文件读取比赛信息
        """
        async with aiofiles.open(path, mode='r', encoding='utf-8') as f:
            contests = await f.read()
            contests = json.loads(contests)
            contests = [Contest.from_dict(contest) for contest in contests['data']]
            return contests

    ###### 对外接口 ######
    async def update(self):
        """
        从网络获取比赛信息并保存到本地文件
        其中对于atcoder，每天只会更新一次，降低被墙的概率
        """
        
        # 由于atcoder_contests是单独限制爬取的，需要单独保存
        atcoder_contests = await self._fetch_atcoder_contest()
        await self._save_contest(atcoder_contests, self.storage_path_atcoder)

        # 所有比赛
        contests = await self._fetch_cf_contest() + \
            await self._fetch_lougu_contest() + \
            await self._fetch_nowcoder_contest() + \
            await self._fetch_leetcode_contest() + \
            await self._read_contest(self.storage_path_atcoder)
        contests.sort(key=lambda x: x.stime)
        await self._save_contest(contests, self.storage_path)
    
    async def read(self) -> list[Contest]:
        """
        从本地文件读取比赛信息
        """
        contests = await self._read_contest(self.storage_path)
        return contests
