#!/usr/bin/env python3
"""
亚马逊产品调研RPA - 快速启动向导
"""
import os
import sys
from pathlib import Path


def print_banner():
    print("="*60)
    print("         亚马逊产品调研RPA - 快速启动向导")
    print("="*60)
    print()


def check_files():
    """检查必要文件"""
    required_files = [
        "feishu_bot.py",
        "integrated_config.py",
        "integrated_service.py",
        "excel_exporter.py",
        "data_processor.py",
    ]
    
    print("📋 检查文件...")
    missing = []
    for f in required_files:
        if os.path.exists(f):
            print(f"  ✓ {f}")
        else:
            print(f"  ✗ {f} (缺失)")
            missing.append(f)
    
    if missing:
        print(f"\n⚠️ 缺失 {len(missing)} 个文件")
    else:
        print("\n✅ 所有文件就绪")
    print()
    return len(missing) == 0


def check_config():
    """检查配置"""
    print("⚙️ 检查配置...")
    
    try:
        from integrated_config import (
            FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_CHAT_ID
        )
        
        configured = True
        if FEISHU_APP_ID == "your_app_id":
            print("  ⚠️ 飞书 App ID 未配置")
            configured = False
        else:
            print("  ✓ App ID 已配置")
            
        if FEISHU_APP_SECRET == "your_app_secret":
            print("  ⚠️ 飞书 App Secret 未配置")
            configured = False
        else:
            print("  ✓ App Secret 已配置")
            
        if FEISHU_CHAT_ID == "your_chat_id":
            print("  ⚠️ Chat ID 未配置")
            configured = False
        else:
            print("  ✓ Chat ID 已配置")
            
        return configured
    except Exception as e:
        print(f"  ✗ 配置检查失败: {e}")
        return False


def show_menu():
    """显示菜单"""
    print("\n📌 请选择:")
    print("  1. 启动整合服务 (推荐)")
    print("  2. 启动简易飞书服务")
    print("  3. 查看配置文件")
    print("  4. 检查依赖")
    print("  0. 退出")
    print()


def start_integrated_service():
    """启动整合服务"""
    print("\n🚀 启动整合服务...")
    print("服务将在 http://localhost:8000 运行")
    print("Webhook地址: http://localhost:8000/feishu/webhook")
    print("\n按 Ctrl+C 停止服务")
    print("-"*60)
    
    try:
        os.system(f"{sys.executable} integrated_service.py")
    except KeyboardInterrupt:
        print("\n服务已停止")


def start_simple_feishu():
    """启动简易服务"""
    print("\n🚀 启动简易服务...")
    print("服务将在 http://localhost:8000 运行")
    print("\n按 Ctrl+C 停止服务")
    print("-"*60)
    
    try:
        os.system(f"{sys.executable} feishu_server.py")
    except KeyboardInterrupt:
        print("\n服务已停止")


def view_config():
    """查看配置"""
    print("\n📝 配置文件: integrated_config.py")
    print("="*60)
    
    try:
        with open("integrated_config.py", "r", encoding="utf-8") as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:50], 1):
                print(f"{i:4}  {line.rstrip()}")
            if len(lines) > 50:
                print(f"      ... (还有 {len(lines) - 50} 行)")
    except Exception as e:
        print(f"读取失败: {e}")


def check_dependencies():
    """检查依赖"""
    print("\n📦 检查依赖...")
    
    dependencies = [
        "fastapi",
        "uvicorn",
        "requests",
        "pandas",
        "openpyxl",
    ]
    
    for dep in dependencies:
        try:
            __import__(dep.replace("-", "_"))
            print(f"  ✓ {dep}")
        except ImportError:
            print(f"  ✗ {dep} (未安装)")
    
    print("\n安装命令: pip install -r requirements.txt")


def main():
    print_banner()
    
    files_ok = check_files()
    config_ok = check_config()
    
    if not files_ok:
        print("\n⚠️ 文件不完整，请检查项目结构")
    elif not config_ok:
        print("\n⚠️ 配置未完成，部分功能将受限")
    
    while True:
        show_menu()
        choice = input("请选择 (0-4): ").strip()
        
        if choice == "1":
            start_integrated_service()
        elif choice == "2":
            start_simple_feishu()
        elif choice == "3":
            view_config()
        elif choice == "4":
            check_dependencies()
        elif choice == "0":
            print("\n👋 再见！")
            break
        else:
            print("\n⚠️ 无效选择")


if __name__ == "__main__":
    main()
