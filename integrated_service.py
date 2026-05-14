#!/usr/bin/env python3
"""
亚马逊产品调研RPA - 整合服务
集成飞书机器人和调研功能
"""
import os
import json
import threading
from datetime import datetime
from fastapi import FastAPI, Request, Response
from feishu_bot import FeishuBot, FeishuAutoReply, FeishuMessageReceiver

try:
    from integrated_config import (
        FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_CHAT_ID,
        AUTO_REPLY_RULES, DEFAULT_KEYWORD
    )
except ImportError:
    FEISHU_APP_ID = "your_app_id"
    FEISHU_APP_SECRET = "your_app_secret"
    FEISHU_CHAT_ID = "your_chat_id"
    AUTO_REPLY_RULES = {}
    DEFAULT_KEYWORD = "water bottle"


app = FastAPI(title="亚马逊产品调研RPA服务", version="2.0")

bot = FeishuBot(app_id=FEISHU_APP_ID, app_secret=FEISHU_APP_SECRET)
auto_reply = FeishuAutoReply(bot)

# 状态管理
class ResearchState:
    def __init__(self):
        self.is_running = False
        self.current_keyword = None
        self.products = []
        self.reports = []
        self.progress = 0
        self.lock = threading.Lock()

state = ResearchState()

# 初始化自动回复规则
if AUTO_REPLY_RULES:
    auto_reply.add_rules_from_dict(AUTO_REPLY_RULES)
else:
    auto_reply.add_rule("你好", "你好！我是亚马逊产品调研RPA机器人 🤖")
    auto_reply.add_rule("帮助", "发送「开始调研」启动产品调研")
    auto_reply.add_rule("开始调研", "正在启动调研，请稍候...")


@app.get("/")
async def root():
    return {
        "service": "亚马逊产品调研RPA",
        "version": "2.0",
        "status": "running",
        "feishu_configured": FEISHU_APP_ID != "your_app_id"
    }


@app.post("/feishu/webhook")
async def feishu_webhook(request: Request):
    """接收飞书消息回调"""
    try:
        body = await request.body()
        print(f"收到消息: {body[:200]}...")
        
        message_info = FeishuMessageReceiver("", "").parse_message(body.decode())
        
        if message_info:
            chat_id = message_info.get("chat_id")
            content = message_info.get("content", "")
            message_type = message_info.get("message_type")
            
            print(f"消息: {content}")
            
            if message_type == "text" and content:
                handle_command(chat_id, content)
        
        return Response(content='{"challenge": "success"}', media_type="application/json")
    except Exception as e:
        print(f"处理异常: {e}")
        return {"status": "error"}


def handle_command(chat_id, message):
    """处理用户命令"""
    message = message.strip()
    
    # 检查是否是特殊命令
    if message.startswith("开始调研"):
        keyword = DEFAULT_KEYWORD
        if len(message.split()) > 1:
            keyword = message.split(maxsplit=1)[1]
        start_research_async(chat_id, keyword)
        return
    
    if message == "状态":
        send_status_update(chat_id)
        return
    
    if message == "报告":
        send_report(chat_id)
        return
    
    if message == "产品池":
        send_products(chat_id)
        return
    
    if message == "配置":
        send_config_info(chat_id)
        return
    
    if message == "清空":
        clear_data(chat_id)
        return
    
    # 检查自动回复规则
    if not auto_reply.process_message(chat_id, message):
        bot.send_text_message(chat_id, "抱歉，我没有理解您的意思。发送「帮助」查看可用命令")


def start_research_async(chat_id, keyword):
    """异步启动调研任务"""
    with state.lock:
        if state.is_running:
            bot.send_text_message(chat_id, "当前有任务正在进行中，请稍候...")
            return
        
        state.is_running = True
        state.current_keyword = keyword
        state.progress = 0
    
    bot.send_card_message(
        chat_id,
        "🚀 启动调研",
        f"开始调研关键词: {keyword}\n\n预计耗时: 5-10分钟\n\n请耐心等待...",
    )
    
    thread = threading.Thread(target=run_research_task, args=(chat_id, keyword))
    thread.daemon = True
    thread.start()


def run_research_task(chat_id, keyword):
    """运行调研任务（后台线程）"""
    try:
        update_progress(chat_id, 10, "正在初始化...")
        
        # 模拟调研流程
        steps = [
            (20, "正在筛选产品..."),
            (40, "正在分析竞品..."),
            (60, "正在分析评论..."),
            (80, "正在生成报告..."),
            (100, "完成！"),
        ]
        
        for progress, status in steps:
            update_progress(chat_id, progress, status)
            import time
            time.sleep(1.5)
        
        # 生成模拟数据
        from excel_exporter import ExcelExporter
        exporter = ExcelExporter()
        
        sample_data = {
            "products": [
                {"asin": "B001", "title": f"{keyword} - 产品1", "price": "$29.99", "rating": "4.5"},
                {"asin": "B002", "title": f"{keyword} - 产品2", "price": "$19.99", "rating": "4.3"},
            ],
            "reviews_analysis": {
                "pain_points": [("break", 30), ("leak", 25)],
                "praise_points": [("durable", 40), ("easy", 35)],
            },
            "keywords": [
                {"keyword": keyword, "search_volume": "50000", "competition": "0.5"},
            ],
        }
        
        report_file = exporter.export_all(sample_data)
        
        with state.lock:
            state.products = sample_data["products"]
            state.reports.append(report_file)
        
        bot.send_card_message(
            chat_id,
            "✅ 调研完成",
            f"关键词: {keyword}\n\n产品数量: {len(state.products)}\n\n报告已生成: {os.path.basename(report_file)}",
        )
        
    except Exception as e:
        bot.send_text_message(chat_id, f"调研失败: {e}")
    finally:
        with state.lock:
            state.is_running = False


def update_progress(chat_id, progress, status):
    """更新进度"""
    state.progress = progress
    print(f"进度: {progress}% - {status}")


def send_status_update(chat_id):
    """发送状态更新"""
    status_text = f"📊 系统状态\n\n"
    if state.is_running:
        status_text += f"🔄 任务进行中\n"
        status_text += f"关键词: {state.current_keyword}\n"
        status_text += f"进度: {state.progress}%\n"
    else:
        status_text += "🟢 空闲中\n"
    
    status_text += f"\n产品池: {len(state.products)} 个产品\n"
    status_text += f"报告数: {len(state.reports)} 份\n"
    
    bot.send_text_message(chat_id, status_text)


def send_report(chat_id):
    """发送报告"""
    if state.reports:
        latest = state.reports[-1]
        bot.send_card_message(
            chat_id,
            "📄 最新报告",
            f"文件: {os.path.basename(latest)}\n\n路径: {latest}",
        )
    else:
        bot.send_text_message(chat_id, "暂无报告，请先启动调研")


def send_products(chat_id):
    """发送产品列表"""
    if state.products:
        text = "📦 当前产品池:\n\n"
        for i, p in enumerate(state.products[:5], 1):
            text += f"{i}. {p['title']}\n   ${p['price']} | {p['rating']}★\n\n"
        if len(state.products) > 5:
            text += f"... 还有 {len(state.products) - 5} 个产品"
        bot.send_text_message(chat_id, text)
    else:
        bot.send_text_message(chat_id, "产品池为空")


def send_config_info(chat_id):
    """发送配置信息"""
    config_text = "⚙️ 当前配置\n\n"
    config_text += f"默认关键词: {DEFAULT_KEYWORD}\n"
    config_text += f"飞书配置: {'已配置' if FEISHU_APP_ID != 'your_app_id' else '未配置'}\n"
    bot.send_text_message(chat_id, config_text)


def clear_data(chat_id):
    """清空数据"""
    with state.lock:
        state.products = []
        state.reports = []
        state.current_keyword = None
    bot.send_text_message(chat_id, "数据已清空")


@app.get("/test")
async def test_endpoint():
    """测试端点"""
    return {"message": "服务正常", "state": {
        "is_running": state.is_running,
        "products": len(state.products),
        "reports": len(state.reports),
    }}


if __name__ == "__main__":
    import uvicorn
    print("="*60)
    print("亚马逊产品调研RPA - 整合服务")
    print("="*60)
    print()
    print("📱 飞书机器人已启动")
    print(f"📝 自动回复规则: {len(auto_reply.rules)} 条")
    print()
    print("🚀 服务地址: http://localhost:8000")
    print("📡 Webhook: http://localhost:8000/feishu/webhook")
    print()
    uvicorn.run(app, host="0.0.0.0", port=8000)
