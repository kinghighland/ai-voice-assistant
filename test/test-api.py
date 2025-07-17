#!/usr/bin/env python3
"""
测试语音助手API的脚本
"""

import requests
import json

API_BASE = "http://localhost:8001"

def test_health():
    """测试健康检查接口"""
    try:
        response = requests.get(f"{API_BASE}/health")
        print("🏥 健康检查:")
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def test_process_command():
    """测试命令处理接口"""
    test_commands = [
        "现在几点了？",
        "打开百度网站",
        "启动计算器",
        "你好，请介绍一下自己"
    ]
    
    for command in test_commands:
        try:
            print(f"\n🧪 测试命令: {command}")
            response = requests.post(
                f"{API_BASE}/process",
                json={
                    "text": command,
                    "execute_commands": True
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ AI回复: {result['ai_response'][:100]}...")
                if result['command_executed']:
                    print(f"   ⚡ 命令执行: {result['command_result']}")
            else:
                print(f"   ❌ 请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")

def main():
    print("🚀 开始测试语音助手API...")
    print("=" * 50)
    
    # 测试健康检查
    if not test_health():
        print("❌ API服务未启动，请先运行: python voice_api_server.py")
        return
    
    # 测试命令处理
    test_process_command()
    
    print("\n" + "=" * 50)
    print("✅ 测试完成！")

if __name__ == "__main__":
    main()