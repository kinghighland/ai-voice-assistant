#!/usr/bin/env python3
"""
快速修改语音助手API端口的脚本
"""

import re
import sys

def change_port(old_port, new_port):
    """修改所有相关文件中的端口号"""
    
    files_to_modify = [
        {
            'file': 'voice_assistant_plugin.js',
            'patterns': [
                (f"'http://localhost:{old_port}'", f"'http://localhost:{new_port}'"),
                (f'"http://localhost:{old_port}"', f'"http://localhost:{new_port}"')
            ]
        },
        {
            'file': 'voice_api_server.py',
            'patterns': [
                (f'port={old_port}', f'port={new_port}')
            ]
        },
        {
            'file': 'docker-compose.yml',
            'patterns': [
                (f'"{old_port}:{old_port}"', f'"{new_port}:{new_port}"')
            ]
        },
        {
            'file': 'Dockerfile',
            'patterns': [
                (f'EXPOSE {old_port}', f'EXPOSE {new_port}')
            ]
        },
        {
            'file': 'test-api.py',
            'patterns': [
                (f'"http://localhost:{old_port}"', f'"http://localhost:{new_port}"')
            ]
        }
    ]
    
    modified_files = []
    
    for file_info in files_to_modify:
        filename = file_info['file']
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            for old_pattern, new_pattern in file_info['patterns']:
                content = content.replace(old_pattern, new_pattern)
            
            if content != original_content:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                modified_files.append(filename)
                print(f"✅ 已修改: {filename}")
            else:
                print(f"⚪ 无需修改: {filename}")
                
        except FileNotFoundError:
            print(f"⚠️  文件不存在: {filename}")
        except Exception as e:
            print(f"❌ 修改失败 {filename}: {e}")
    
    return modified_files

def main():
    if len(sys.argv) != 3:
        print("使用方法: python change_port.py <旧端口> <新端口>")
        print("例如: python change_port.py 8001 8002")
        return
    
    try:
        old_port = int(sys.argv[1])
        new_port = int(sys.argv[2])
    except ValueError:
        print("❌ 端口号必须是数字")
        return
    
    if not (1024 <= new_port <= 65535):
        print("❌ 端口号应该在1024-65535范围内")
        return
    
    print(f"🔄 将端口从 {old_port} 修改为 {new_port}")
    print("=" * 40)
    
    modified_files = change_port(old_port, new_port)
    
    print("=" * 40)
    if modified_files:
        print(f"✅ 成功修改了 {len(modified_files)} 个文件")
        print("\n📝 接下来需要:")
        print("1. 重新构建Docker镜像: docker-compose build")
        print("2. 重启服务: docker-compose up -d")
        print(f"3. 访问新地址: http://localhost:{new_port}")
    else:
        print("⚪ 没有文件需要修改")

if __name__ == "__main__":
    main()