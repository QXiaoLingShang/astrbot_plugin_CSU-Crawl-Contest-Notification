"""
HTML模板模块
严格按照main-backup中的实现，包含图片报告和PDF报告的不同HTML模板
"""


class HTMLTemplates:
    """HTML模板管理类（适配中南大学创新竞赛通知报告）"""

    @staticmethod
    def get_image_template() -> str:
        """获取图片报告的HTML模板（使用{{ }}占位符）"""
        return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>中南大学创新竞赛通知报告</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Noto Sans SC', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            min-height: 100vh;
            padding: 30px;
            line-height: 1.6;
            color: #1a1a1a;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
            color: #ffffff;
            padding: 60px 50px;
            text-align: center;
            border-radius: 30px 30px 0 0;
        }

        .header h1 {
            font-size: 2.8em;
            font-weight: 700;
            margin-bottom: 16px;
            letter-spacing: -0.5px;
        }

        .header .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
            font-weight: 300;
            letter-spacing: 0.5px;
        }

        .content {
            padding: 50px;
        }

        .section {
            margin-bottom: 60px;
        }

        .section-title {
            font-size: 1.8em;
            font-weight: 600;
            margin-bottom: 30px;
            color: #1e40af;
            letter-spacing: -0.3px;
            display: flex;
            align-items: center;
            gap: 12px;
            border-bottom: 3px solid #dbeafe;
            padding-bottom: 12px;
        }

        .section-title i {
            font-style: normal;
            background: #3b82f6;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 25px;
            margin-bottom: 40px;
        }

        .stat-card {
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            padding: 35px 25px;
            text-align: center;
            border-radius: 15px;
            border: 1px solid #bfdbfe;
            transition: all 0.3s ease;
        }

        .stat-number {
            font-size: 3em;
            font-weight: 700;
            color: #1e40af;
            margin-bottom: 8px;
            display: block;
            letter-spacing: -1px;
        }

        .stat-label {
            font-size: 1.1em;
            color: #3b82f6;
            font-weight: 500;
            letter-spacing: 0.5px;
        }

        /* 通知列表样式 */
        .notices-list {
            display: grid;
            gap: 18px;
        }

        
        /* 新增：标题容器样式，实现中间填充 */
        .notice-title-wrapper {
            flex: 1;
            margin: 0 12px; /* 与序号、日期的间距 */
            overflow: hidden;
        }

        .notice-title-wrapper a {
            color: #1e40af;
            text-decoration: none;
            font-weight: 600;
            font-size: 18px;
            line-height: 1.5;
            white-space: nowrap; /* 禁止标题换行 */
            overflow: hidden;
            text-overflow: ellipsis; /* 超出部分显示省略号 */
            display: block;
        }

        .notice-item {
            background: #ffffff;
            padding: 12px 22px;
            border-radius: 12px;
            border-left: 4px solid #3b82f6;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
        }

        .notice-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            /* margin-bottom: 12px; */
        }

        .notice-number {
            background: #3b82f6;
            color: white;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 0.9em;
            font-weight: 500;
        }

        .notice-date {
            color: #64748b;
            font-size: 0.95em;
            font-weight: 400;
        }

        .notice-title a {
            color: #1e40af;
            text-decoration: none;
            font-weight: 600;
            font-size: 1.15em;
            line-height: 1.5;
            display: block;
        }

    



        .footer {
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
            color: #ffffff;
            text-align: center;
            padding: 40px;
            font-size: 1em;
            font-weight: 300;
            letter-spacing: 0.5px;
            opacity: 0.9;
        }

        @media (max-width: 768px) {
            body {
                padding: 15px;
            }

            .container {
                max-width: 100%;
            }

            .header {
                padding: 30px 25px;
            }

            .header h1 {
                font-size: 2em;
            }

            .content {
                padding: 25px;
            }

            .stats-grid {
                grid-template-columns: 1fr 1fr;
                gap: 15px;
            }

            .stat-number {
                font-size: 2.2em;
            }

            .notice-title a {
                font-size: 1em;
            }
        }

        @media (max-width: 480px) {
            .stats-grid {
                grid-template-columns: 1fr;
            }

            .section-title {
                font-size: 1.5em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📢 中南大学创新竞赛通知报告</h1>
            <div class="subtitle">报告生成时间：{{ report_time }}</div>
        </div>
        <div class="content">
            <div class="section">
                <h2 class="section-title"><i>📊</i> 报告概览</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">{{ notice_count }}</div>
                        <div class="stat-label">通知总数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{{ latest_update }}</div>
                        <div class="stat-label">最新通知日期</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{{ report_time.split(' ')[0] }}</div>
                        <div class="stat-label">报告生成日期</div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2 class="section-title"><i>📋</i> 通知列表（按时间倒序）<span class="subtitle">（第 {{ page }} 页，每页 {{ list_len }} 条）</span></h2>
                <div class="notices-list">
                    {{ notices_html | safe }}
                </div>
            </div>
        </div>
        <div class="footer">
            数据来源：中南大学创新创业学院 | 链接：https://bksy.csu.edu.cn/tztg/cxycyjybgs.htm
        </div>
    </div>
</body>
</html>"""

    @staticmethod
    def get_new_image_template():
        """获取新增的HTML模板（使用{{ }}占位符）"""
        return """<!DOCTYPE html>
            <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>今日新增通知</title>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Noto Sans SC', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                min-height: 100vh;
                padding: 30px;
                line-height: 1.6;
                color: #1a1a1a;
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 20px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
                overflow: hidden;
            }

            .content {
                padding: 50px;
            }

            .section {
                margin-bottom: 20px;
            }

            .section-title {
                font-size: 1.8em;
                font-weight: 600;
                margin-bottom: 30px;
                color: #1e40af;
                letter-spacing: -0.3px;
                display: flex;
                align-items: center;
                gap: 12px;
                border-bottom: 3px solid #dbeafe;
                padding-bottom: 12px;
            }

            .section-title i {
                font-style: normal;
                background: #3b82f6;
                color: white;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            
            .header {
                background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
                color: #ffffff;
                padding: 60px 50px;
                text-align: center;
                border-radius: 30px 30px 0 0;
            }

            .header h1 {
                font-size: 2.8em;
                font-weight: 700;
                margin-bottom: 16px;
                letter-spacing: -0.5px;
            }

            .header .subtitle {
                font-size: 1.2em;
                opacity: 0.9;
                font-weight: 300;
                letter-spacing: 0.5px;
            }

            /* 通知列表样式 */
            .notices-list {
                display: grid;
                gap: 18px;
            }

            .notice-item {
                background: #ffffff;
                padding: 12px 22px;
                border-radius: 12px;
                border-left: 4px solid #3b82f6;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
                transition: all 0.3s ease;
            }

            .notice-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
            }

            
            .notice-number {
                background: #3b82f6;
                color: white;
                width: 28px;
                height: 28px;
                border-radius: 50%;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-size: 0.9em;
                font-weight: 500;
            }

            .notice-title-wrapper {
                flex: 1;
                margin: 0 12px; /* 与序号、日期的间距 */
                overflow: hidden;
            }

            .notice-title-wrapper a {
                color: #1e40af;
                text-decoration: none;
                font-weight: 600;
                font-size: 18px;
                line-height: 1.5;
                white-space: nowrap; /* 禁止标题换行 */
                overflow: hidden;
                text-overflow: ellipsis; /* 超出部分显示省略号 */
                display: block;
            }

            .notice-date {
                color: #64748b;
                font-size: 0.95em;
                font-weight: 400;
            }

            .notice-title a {
                color: #1e40af;
                text-decoration: none;
                font-weight: 600;
                font-size: 1.15em;
                line-height: 1.5;
                display: block;
            }

            .footer {
                background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
                color: #ffffff;
                text-align: center;
                padding: 10px;
                font-size: 1em;
                font-weight: 300;
                letter-spacing: 0.5px;
                opacity: 0.9;
            }

            @media (max-width: 768px) {
                body {
                    padding: 15px;
                }

                .container {
                    max-width: 100%;
                }

                .header {
                    padding: 30px 25px;
                }

                .header h1 {
                    font-size: 2em;
                }

                .content {
                    padding: 25px;
                }

                .notice-title a {
                    font-size: 1em;
                }
            }

            @media (max-width: 480px) {
                .section-title {
                    font-size: 1.5em;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">

            <div class="header">
                <h1>📢 中南大学创新竞赛通知报告</h1>
                <div class="subtitle">报告生成时间：{{ report_time }}</div>
            </div>
            <div class="content">

                <div class="section">
                    <h2 class="section-title"><i>📋</i> 今日新增</h2>
                    <div class="notices-list">
                        {{ notices_html | safe }}
                    </div>
                </div>
            </div>
            <div class="footer">
                数据来源：中南大学创新创业学院 | 链接：https://bksy.csu.edu.cn/tztg/cxycyjybgs.htm
            </div>
        </div>
    </body>
    </html>

            """