#!/usr/bin/env python3
"""
同步项目到GitHub的脚本
"""

import subprocess
import sys
import os

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description}成功")
            if result.stdout.strip():
                print(f"   输出: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description}失败")
            if result.stderr.strip():
                print(f"   错误: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description}异常: {e}")
        return False

def check_git_status():
    """检查Git状态"""
    print("📊 检查Git状态...")
    run_command("git status", "查看Git状态")

def sync_to_github():
    """同步到GitHub"""
    print("🚀 开始同步到GitHub...")
    print("=" * 50)
    
    # 检查是否在Git仓库中
    if not os.path.exists('.git'):
        print("📁 初始化Git仓库...")
        if not run_command("git init", "初始化Git仓库"):
            return False
    
    # 检查远程仓库
    result = subprocess.run("git remote -v", shell=True, capture_output=True, text=True)
    if "github.com/kinghighland" not in result.stdout:
        print("🔗 添加GitHub远程仓库...")
        repo_url = input("请输入GitHub仓库URL (例: https://github.com/kinghighland/ai-voice-assistant.git): ")
        if not repo_url:
            repo_url = "https://github.com/kinghighland/ai-voice-assistant.git"
        
        if not run_command(f"git remote add origin {repo_url}", "添加远程仓库"):
            # 如果已存在，尝试更新
            run_command(f"git remote set-url origin {repo_url}", "更新远程仓库URL")
    
    # 添加所有文件
    if not run_command("git add .", "添加文件到暂存区"):
        return False
    
    # 检查是否有更改
    result = subprocess.run("git diff --cached --quiet", shell=True)
    if result.returncode == 0:
        print("ℹ️  没有新的更改需要提交")
        check_git_status()
        return True
    
    # 提交更改
    commit_message = input("请输入提交信息 (默认: 更新语音助手项目): ")
    if not commit_message:
        commit_message = "更新语音助手项目"
    
    if not run_command(f'git commit -m "{commit_message}"', "提交更改"):
        return False
    
    # 推送到GitHub
    print("📤 推送到GitHub...")
    
    # 首次推送可能需要设置上游分支
    result = subprocess.run("git push origin main", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("🔄 尝试推送到master分支...")
        result = subprocess.run("git push origin master", shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print("🔄 尝试设置上游分支...")
            if not run_command("git push -u origin main", "推送并设置上游分支"):
                run_command("git push -u origin master", "推送到master分支")
    else:
        print("✅ 推送成功")
    
    return True

def main():
    print("🎤 AI语音助手 - GitHub同步工具")
    print("=" * 50)
    
    # 检查当前状态
    check_git_status()
    
    # 确认同步
    confirm = input("\n是否继续同步到GitHub? (y/N): ")
    if confirm.lower() not in ['y', 'yes']:
        print("❌ 取消同步")
        return
    
    # 执行同步
    if sync_to_github():
        print("\n" + "=" * 50)
        print("🎉 同步完成！")
        print("📍 项目地址: https://github.com/kinghighland/ai-voice-assistant")
        print("\n📋 接下来你可以:")
        print("1. 访问GitHub仓库查看项目")
        print("2. 设置仓库描述和标签")
        print("3. 创建Release版本")
        print("4. 邀请其他开发者协作")
    else:
        print("\n❌ 同步失败，请检查错误信息")

if __name__ == "__main__":
    main()