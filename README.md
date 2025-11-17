# CSU创新创业竞赛通知爬取

一个个人自用的AstrBot插件，用于定时从官网爬取CSU的通知并发送到指定QQ群聊。
用来解决长期查看官网通知的需求。

注：该插件的核心逻辑修改自[astrbot-qq-group-daily-analysis](https://github.com/SXP-Simon/astrbot-qq-group-daily-analysis)

## 功能

- 定时从官网爬取CSU的通知（官网链接：[CSU Contest Notification](https://bksy.csu.edu.cn/tztg/cxycyjybgs.htm)）
- 支持本地缓存，避免重复发送相同通知
- 支持定时更新推送新的通知
- 支持指令查询本地缓存的通知


## 待添加功能

- [ ] 定时推送各种编程比赛


## 数据来源

- CSU的比赛通知
     - [CSU Contest Notification](https://bksy.csu.edu.cn/tztg/cxycyjybgs.htm)
- 各种编程比赛通知
     - [Codeforces](https://codeforces.com/api/contest.list)
     - [LuoGu](https://www.luogu.com.cn/contest/list?page=1&_contentOnly=1)
     - 