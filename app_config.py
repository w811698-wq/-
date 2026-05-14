# ============================================
# 飞书应用配置
# ============================================

# 企业自建应用凭证
FEISHU_APP_ID = "cli_a92f075758219cc9"
FEISHU_APP_SECRET = "JbC7wfZxO4cNli12hbTv5YYhdpMrhxsv"

# 机器人配置
BOT_NAME = "亚马逊调研RPA"
BOT_DESCRIPTION = "亚马逊产品调研自动化机器人"

# 接收消息的群组ID或用户ID
# 可以是 open_id, user_id, union_id, email, chat_id
DEFAULT_RECEIVER_ID = ""  # 如果为空，将发送给应用自身

# ============================================
# 应用权限配置
# ============================================
# 需要在飞书开放平台为应用添加以下权限:
# - im:message:send_as_bot (发送消息)
# - im:message (读取消息)

# ============================================
# 其他配置
# ============================================
ENABLE_VERIFICATION = False
ENABLE_ENCRYPTION = False
ENCRYPT_KEY = ""
