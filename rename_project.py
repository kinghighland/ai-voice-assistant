#!/usr/bin/env python3
"""
重命名项目文件夹的脚本
"""

import os
import shutil
import sys

def rename_project():
    """重命名项目文件夹"""
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    current_folder_name = os.path.basename(current_dir)
    new_folder_name = "ai-voice-assistant"
    new_path = os.path.join(parent_dir, new_folder_name)
    
    print(f"🔄 项目重命名工具")
    print("=" * 50)
    print(f"当前文件夹: {current_folder_name}")
    print(f"目标文件夹: {new_folder_name}")
    print(f"当前路径: {current_dir}")
    print(f"目标路径: {new_path}")
    
    if current_folder_name == new_folder_name:
        print("✅ 文件夹名称已经正确，无需重命名")
        return True
    
    if os.path.exists(new_path):
        print(f"❌ 目标文件夹 {new_folder_name} 已存在")
        overwrite = input("是否覆盖? (y/N): ")
        if overwrite.lower() not in ['y', 'yes']:
            return False
        shutil.rmtree(new_path)
    
    try:
        print(f"🔄 重命名文件夹...")
        os.rename(current_dir, new_path)
        print(f"✅ 重命名成功！")
        print(f"📁 新路径: {new_path}")
        print("\n📋 接下来请:")
        print(f"1. cd {new_path}")
        print("2. python sync_to_github.py")
        return True
    except Exception as e:
        print(f"❌ 重命名失败: {e}")
        return False

if __name__ == "__main__":
    rename_project()