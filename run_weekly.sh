#!/bin/bash
# =====================================================
# 亚马逊假发类目BSR排名周报 - 一键执行脚本
# 用法: bash run_weekly.sh
# 定时任务: 每周一 09:00 执行
# =====================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/data/weekly_report.log"

echo "====================================================" | tee -a "$LOG_FILE"
echo "  亚马逊BSR周报 - 自动执行" | tee -a "$LOG_FILE"
echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "====================================================" | tee -a "$LOG_FILE"

cd "$SCRIPT_DIR"

# Step 1: 使用WebFetch获取最新BSR数据
echo ""
echo "[Step 1/3] 获取最新BSR页面数据..." | tee -a "$LOG_FILE"
python3 fetch_data.py 2>&1 | tee -a "$LOG_FILE"

# Step 2: 如果curl被拦截，提示手动获取
if [ ! -s "data/html/hair_extensions.txt" ] || [ ! -s "data/html/hairpieces.txt" ]; then
    echo ""
    echo "⚠️ 自动抓取可能被Amazon反爬拦截" | tee -a "$LOG_FILE"
    echo "需要手动获取数据，请按以下步骤操作：" | tee -a "$LOG_FILE"
    echo "1. 使用WebFetch获取以下URL的内容：" | tee -a "$LOG_FILE"
    echo "   - https://www.amazon.com/Best-Sellers-Beauty-Personal-Care-Hair-Extensions/zgbs/beauty/702379011" | tee -a "$LOG_FILE"
    echo "   - https://www.amazon.com/Best-Sellers-Hairpieces/zgbs/beauty/702380011" | tee -a "$LOG_FILE"
    echo "2. 将内容保存到 data/html/ 目录" | tee -a "$LOG_FILE"
    echo "3. 重新运行此脚本" | tee -a "$LOG_FILE"
    exit 1
fi

# Step 3: 生成周报并发送飞书
echo ""
echo "[Step 2/3] 解析数据、生成周报..." | tee -a "$LOG_FILE"
python3 bsr_weekly_report.py 2>&1 | tee -a "$LOG_FILE"

echo ""
echo "[Step 3/3] 完成!" | tee -a "$LOG_FILE"
echo "====================================================" | tee -a "$LOG_FILE"
