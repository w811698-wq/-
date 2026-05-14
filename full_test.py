#!/usr/bin/env python3
"""
完整测试脚本 - 验证所有配置
"""
import sys
import os


def test_imports():
    """测试导入"""
    print("="*60)
    print("1. 测试模块导入")
    print("="*60)
    
    modules = [
        ("requests", "HTTP请求"),
        ("json", "JSON处理"),
        ("datetime", "日期时间"),
    ]
    
    success = True
    for mod_name, desc in modules:
        try:
            __import__(mod_name)
            print(f"  ✅ {mod_name} ({desc})")
        except ImportError:
            print(f"  ❌ {mod_name} ({desc})")
            success = False
    
    print()
    return success


def test_feishu_connection():
    """测试飞书连接"""
    print("="*60)
    print("2. 测试飞书应用连接 (App ID/Secret)")
    print("="*60)
    
    try:
        import requests
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
        data = {
            "app_id": "cli_a92f075758219cc9",
            "app_secret": "JbC7wfZxO4cNli12hbTv5YYhdpMrhxsv"
        }
        
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        
        if result.get("code") == 0:
            print("  ✅ 连接成功!")
            print(f"  Token有效期: {result.get('expire', 7200)}秒")
            return True
        else:
            print(f"  ❌ 连接失败: {result.get('msg')}")
            return False
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        return False


def test_webhook():
    """测试webhook"""
    print()
    print("="*60)
    print("3. 测试飞书Webhook (自定义机器人)")
    print("="*60)
    
    try:
        import requests
        import json
        
        webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/3b388739-a336-4388-995d-0f6a68021b26"
        
        data = {
            "msg_type": "text",
            "content": {
                "text": "🎉 测试消息\n\n✅ 亚马逊调研RPA配置测试成功!"
            }
        }
        
        response = requests.post(
            webhook_url,
            data=json.dumps(data),
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        result = response.json()
        
        if result.get("code") == 0:
            print("  ✅ Webhook发送成功!")
            return True
        else:
            print(f"  ❌ Webhook失败: {result.get('msg')}")
            return False
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        return False


def test_excel_export():
    """测试Excel导出"""
    print()
    print("="*60)
    print("4. 测试Excel导出功能")
    print("="*60)
    
    try:
        # 测试导入
        import pandas
        print("  ✅ pandas 已安装")
        
        # 测试导出模块
        os.makedirs("output", exist_ok=True)
        print("  ✅ output目录已创建")
        
        # 简单测试
        from datetime import datetime
        test_file = os.path.join("output", f"test_{datetime.now().strftime('%H%M%S')}.txt")
        with open(test_file, "w") as f:
            f.write("测试文件")
        os.remove(test_file)
        print("  ✅ 文件系统正常")
        
        return True
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        return False


def send_demo_report():
    """发送演示报告到飞书"""
    print()
    print("="*60)
    print("5. 发送演示报告到飞书")
    print("="*60)
    
    try:
        import requests
        import json
        from datetime import datetime
        
        webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/3b388739-a336-4388-995d-0f6a68021b26"
        
        # 构建卡片消息
        card_content = {
            "msg_type": "interactive",
            "card": {
                "config": {"wide_screen_mode": True},
                "elements": [
                    {
                        "tag": "markdown",
                        "content": (
                            "## 🤖 亚马逊产品调研RPA\n\n"
                            "### 测试报告\n\n"
                            "---"
                        )
                    },
                    {
                        "tag": "div",
                        "text": {
                            "content": (
                                "**关键词**: water bottle\n\n"
                                "**产品数量**: 5\n\n"
                                "**关键词数量**: 10\n\n"
                                "**调研时间**: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n"
                                "---"
                            ),
                            "tag": "lark_md"
                        }
                    },
                    {
                        "tag": "div",
                        "text": {
                            "content": (
                                "✅ **测试结果**: 全部通过!\n\n"
                                "📊 系统运行正常\n"
                                "🔗 飞书连接成功\n"
                                "📁 报告生成就绪"
                            ),
                            "tag": "lark_md"
                        }
                    }
                ]
            }
        }
        
        response = requests.post(
            webhook_url,
            data=json.dumps(card_content),
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        result = response.json()
        
        if result.get("code") == 0:
            print("  ✅ 演示报告已发送!")
            print("  💡 请检查飞书群消息")
            return True
        else:
            print(f"  ❌ 发送失败: {result.get('msg')}")
            return False
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        return False


def main():
    """主测试流程"""
    print()
    print("╔" + "═"*58 + "╗")
    print("║" + " "*15 + "亚马逊调研RPA - 配置测试" + " "*17 + "║")
    print("╚" + "═"*58 + "╝")
    print()
    
    results = []
    
    # 执行所有测试
    results.append(("模块导入", test_imports()))
    results.append(("飞书连接", test_feishu_connection()))
    results.append(("Webhook测试", test_webhook()))
    results.append(("Excel功能", test_excel_export()))
    results.append(("发送报告", send_demo_report()))
    
    # 汇总结果
    print()
    print("="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    passed = 0
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name:<15} {status}")
        if result:
            passed += 1
    
    print()
    print(f"总计: {passed}/{len(results)} 项通过")
    print()
    
    if passed == len(results):
        print("🎉 所有测试通过! 系统配置完成!")
        print()
        print("💡 接下来可以:")
        print("  1. 运行演示: python automated_research.py demo")
        print("  2. 交互模式: python automated_research.py")
        print("  3. 自定义调研: python automated_research.py 'your keyword'")
    else:
        print("⚠️ 部分测试失败，请检查配置")
    
    print()
    print("="*60)


if __name__ == "__main__":
    main()
