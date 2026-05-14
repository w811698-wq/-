#!/usr/bin/env python3
"""
飞书机器人演示脚本
展示消息发送和自动回复功能
"""
import os
import sys


def show_usage():
    """显示使用说明"""
    print("="*60)
    print("飞书机器人演示")
    print("="*60)
    print()
    print("功能说明:")
    print("  1. FeishuBot - 飞书消息发送模块")
    print("     - send_text_message()   发送文本消息")
    print("     - send_card_message()   发送卡片消息")
    print("     - send_image_message()  发送图片消息")
    print()
    print("  2. FeishuAutoReply - 自动回复模块")
    print("     - add_rule()           添加回复规则")
    print("     - process_message()    处理消息并自动回复")
    print()
    print("  3. FeishuMessageReceiver - 消息接收模块")
    print("     - verify_request()     验证请求合法性")
    print("     - parse_message()      解析消息内容")
    print()
    print("配置步骤:")
    print("  1. 在飞书开发者平台创建企业自建应用")
    print("  2. 获取 App ID 和 App Secret")
    print("  3. 启用 '机器人' 能力")
    print("  4. 添加机器人到群组")
    print("  5. 获取群组的 chat_id")
    print()
    print("使用示例:")
    print("""
from feishu_bot import FeishuBot, FeishuAutoReply

# 初始化机器人
bot = FeishuBot(app_id="your_app_id", app_secret="your_app_secret")

# 发送文本消息
bot.send_text_message(chat_id="your_chat_id", text="你好！")

# 设置自动回复规则
auto_reply = FeishuAutoReply(bot)
auto_reply.add_rule("你好", "你好！我是飞书机器人~")
auto_reply.add_rule("帮助", "请问需要什么帮助？")

# 处理消息
auto_reply.process_message(chat_id="your_chat_id", message="你好")
""")
    print("="*60)


def generate_sample_config():
    """生成示例配置文件"""
    config_content = '''# 飞书机器人配置文件
# 请在飞书开发者平台获取以下信息

FEISHU_APP_ID = "your_app_id_here"
FEISHU_APP_SECRET = "your_app_secret_here"
FEISHU_CHAT_ID = "your_chat_id_here"

# 自动回复规则
AUTO_REPLY_RULES = {
    "你好": "你好！我是亚马逊产品调研RPA机器人~",
    "帮助": "请问需要什么帮助？\n\n可用命令:\n- 开始调研: 启动产品调研\n- 状态: 查看调研进度\n- 报告: 获取最新报告\n- 帮助: 显示帮助信息",
    "开始调研": "正在启动亚马逊产品调研，请稍候...",
    "状态": "当前无正在进行的调研任务",
    "报告": "最新调研报告已发送至群组",
    "再见": "再见！如有需要随时召唤我~"
}
'''
    config_path = os.path.join(os.path.dirname(__file__), 'feishu_config.py')
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    print(f"✓ 配置文件已生成: {config_path}")
    return config_path


def main():
    print("="*60)
    print("飞书机器人 - 消息发送与自动回复")
    print("="*60)
    print()
    
    print("[1/3] 模块功能介绍")
    show_usage()
    print()
    
    print("[2/3] 生成配置文件...")
    config_path = generate_sample_config()
    print()
    
    print("[3/3] 快速开始")
    print("请按照以下步骤配置:")
    print(f"  1. 编辑配置文件: {config_path}")
    print("  2. 替换 App ID、App Secret、Chat ID")
    print("  3. 运行: python feishu_server.py")
    print()
    print("需要帮助？请查看 README.md 或联系管理员")


if __name__ == "__main__":
    main()
