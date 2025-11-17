"""
比赛类
"""

import json
import time

# 比赛类
class Contest:
    def __init__(self, oj: str = '', name: str = '', stime: int = 0, dtime: int = 0, etime: int = 0,
                 link: str = ''):
        self.oj = oj
        self.name = name
        self.stime = stime
        self.etime = etime
        self.dtime = dtime
        self.link = link

        

    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=False, indent=4)

    def __repr__(self):
        return json.dumps(self.__dict__, ensure_ascii=False, indent=4)
    

    @classmethod
    def from_dict(cls, data: dict) -> 'Contest':
        """从字典初始化 Contest 实例"""
        return cls(
            oj=data.get("oj", ""),
            name=data.get("name", ""),
            stime=data.get("stime", 0),
            etime=data.get("etime", 0),
            dtime=data.get("dtime", 0),
            link=data.get("link", "")
        )
    
    @classmethod
    def timestamp_to_time(cls, timestamp: int) -> str:
        """将时间戳转换为正常时间字符串"""
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    
    @classmethod
    def dtime_to_time(cls, dtime: int) -> str:
        """将持续时间转换为正常时间字符串，且看情况省略分钟和秒"""
        hour = dtime // 3600
        minute = (dtime % 3600) // 60
        second = dtime % 60
        newTime = ''
        if hour != 0:
            newTime += f"{hour}小时"
        if minute != 0:
            newTime += f"{minute}分钟"
        if second != 0:
            newTime += f"{second}秒"
        return newTime
