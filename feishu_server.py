#!/usr/bin/env python3
"""
飞书机器人消息接收服务
基于FastAPI实现消息监听和自动回复
"""
import os
from fastapi import FastAPI, Request, Response
from feishu_bot import FeishuBot, FeishuAutoReply, FeishuMessageReceiver

try:
    from feishu_config import FEISHU_APP_ID, FEISHU_APP_SECRET, AUTO_REPLY_RULES
except ImportError:
    FEISHU_APP_ID = "your_app_id"
    FEISHU_APP_SECRET = "your_app_secret"
    AUTO_REPLY_RULES = {}

app = FastAPI(title="飞书机器人服务", version="1.0")

bot = FeishuBot(app_id=FEISHU_APP_ID, app_secret=FEISHU_APP_SECRET)
auto_reply = FeishuAutoReply(bot)

if AUTO_REPLY_RULES:
    auto_reply.add_rules_from_dict(AUTO_REPLY_RULES)
else:
    auto_reply.add_rule("你好", "你好！我是亚马逊产品调研RPA机器人~")
    auto_reply.add_rule("帮助", "请问需要什么帮助？")
    auto_reply.add_rule("开始调研", "正在启动亚马逊产品调研，请稍候...")
    auto_reply.add_rule("状态", "当前无正在进行的调研任务")
    auto_reply.add_rule("报告", "最新调研报告已发送至群组")


@app.get("/")
async def root():
    return {"message": "飞书机器人服务运行中"}


@app.post("/feishu/webhook")
async def feishu_webhook(request: Request):
    """接收飞书消息回调"""
    try:
        body = await request.body()
        headers = dict(request.headers)
        
        print(f"收到消息: {body[:200]}...")
        
        message_info = FeishuMessageReceiver("", "").parse_message(body.decode())
        
        if message_info:
            chat_id = message_info.get("chat_id")
            content = message_info.get("content", "")
            message_type = message_info.get("message_type")
            
            print(f"消息类型: {message_type}, 内容: {content}")
            
            if message_type == "text" and content:
                auto_reply.process_message(chat_id, content)
        
        return Response(content='{"challenge": "success"}', media_type="application/json")
    
    except Exception as e:
        print(f"处理消息异常: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/send_message")
async def send_message(chat_id: str, text: str):
    """手动发送消息"""
    result = bot.send_text_message(chat_id, text)
    return {"success": result, "message": "消息发送成功" if result else "消息发送失败"}


@app.get("/send_card")
async def send_card(chat_id: str, title: str = "通知", content: str = "内容"):
    """手动发送卡片消息"""
    result = bot.send_card_message(chat_id, title, content)
    return {"success": result, "message": "卡片发送成功" if result else "卡片发送失败"}


@app.get("/rules")
async def list_rules():
    """查看当前的回复规则"""
    return {"rules": auto_reply.rules}


@app.post("/add_rule")
async def add_rule(keyword: str, reply_text: str, match_type: str = "contains"):
    """添加新的回复规则"""
    auto_reply.add_rule(keyword, reply_text, match_type)
    return {"success": True, "message": f"规则添加成功: '{keyword}' -> '{reply_text}'"}


if __name__ == "__main__":
    import uvicorn
    print("启动飞书机器人服务...")
    print(f"自动回复规则数量: {len(auto_reply.rules)}")
    for rule in auto_reply.rules:
        print(f"  - {rule['keyword']}: {rule['reply_text'][:30]}...")
    print()
    uvicorn.run(app, host="0.0.0.0", port=8000)
