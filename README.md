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

## 更新日志

<details>
<summary>📋 点击展开查看完整更新日志</summary>


### v1.0.3
- 正在重构，无新增内容

### v1.0.2
- 添加了爬取各种算法比赛通知的功能
  - 使用指令：测试比赛 \[days\] \[hours\] \[minutes\] \[seconds\]
  - 自动返回days、hours、minutes、seconds内的所有比赛通知（默认3天）
  - 平台包括：Codeforces、LuoGu、AtCoder、NowCode、LeetCode等

## 数据来源

- CSU的比赛通知
     - [CSU Contest Notification](https://bksy.csu.edu.cn/tztg/cxycyjybgs.htm)
- 各种编程比赛通知
     - [Codeforces](https://codeforces.com/api/contest.list)
     - [LuoGu](https://www.luogu.com.cn/contest/list?page=1&_contentOnly=1)
     - 