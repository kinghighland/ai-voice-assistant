#!/usr/bin/env python3
"""
使用ModelScope快速下载Whisper模型
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_modelscope():
    """检查ModelScope是否安装"""
    try:
        result = subprocess.run(['modelscope', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ ModelScope已安装: {result.stdout.strip()}")
            return True
        else:
            return False
    except FileNotFoundError:
        return False

def install_modelscope():
    """安装ModelScope"""
    print("📦 正在安装ModelScope...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'modelscope'], check=True)
        print("✅ ModelScope安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ModelScope安装失败: {e}")
        return False

def download_whisper_model(model_name):
    """下载Whisper模型"""
    model_mapping = {
        "large-v3": "iic/Whisper-large-v3",
        "large-v3-turbo": "iic/Whisper-large-v3-turbo"
    }
    
    if model_name not in model_mapping:
        print(f"❌ 不支持的模型: {model_name}")
        return False
    
    modelscope_model = model_mapping[model_name]
    print(f"🚀 开始下载模型: {modelscope_model}")
    
    try:
        # 使用ModelScope下载
        cmd = ['modelscope', 'download', '--model', modelscope_model]
        print(f"执行命令: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 模型下载完成")
        print(f"下载路径: {result.stdout.strip()}")
        
        # 获取下载路径
        download_path = result.stdout.strip()
        return setup_whisper_cache(download_path, model_name)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 模型下载失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def setup_whisper_cache(download_path, model_name):
    """设置Whisper缓存"""
    whisper_cache = Path.home() / ".cache" / "whisper"
    whisper_cache.mkdir(parents=True, exist_ok=True)
    
    # 查找模型文件
    download_dir = Path(download_path)
    model_files = list(download_dir.glob("*.pt"))
    
    if not model_files:
        print(f"❌ 在 {download_path} 中未找到.pt模型文件")
        return False
    
    model_file = model_files[0]
    target_file = whisper_cache / f"{model_name}.pt"
    
    try:
        # 复制或链接模型文件
        if target_file.exists():
            print(f"⚠️ 目标文件已存在: {target_file}")
            response = input("是否覆盖? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                return True
        
        shutil.copy2(model_file, target_file)
        print(f"✅ 模型文件已复制到: {target_file}")
        print(f"📊 文件大小: {target_file.stat().st_size / 1024**3:.1f} GB")
        
        return True
        
    except Exception as e:
        print(f"❌ 设置缓存失败: {e}")
        return False

def main():
    """主函数"""
    print("🎤 Whisper模型快速下载工具 (ModelScope)")
    print("=" * 50)
    
    # 检查ModelScope
    if not check_modelscope():
        print("❌ ModelScope未安装")
        response = input("是否安装ModelScope? (Y/n): ")
        if response.lower() in ['', 'y', 'yes']:
            if not install_modelscope():
                return
        else:
            print("👋 退出")
            return
    
    # 选择模型
    models = {
        "1": ("large-v3-turbo", "推荐: 显存占用少，速度快"),
        "2": ("large-v3", "最佳质量，显存占用大")
    }
    
    print("\n可用模型:")
    for key, (name, desc) in models.items():
        print(f"  {key}. {name} - {desc}")
    
    choice = input("\n请选择模型 (1-2, 默认1): ").strip() or "1"
    
    if choice in models:
        model_name, desc = models[choice]
        print(f"\n准备下载: {model_name}")
        print(f"描述: {desc}")
        
        confirm = input("是否继续? (Y/n): ").strip().lower()
        if confirm in ['', 'y', 'yes']:
            success = download_whisper_model(model_name)
            
            if success:
                print(f"\n🎉 模型 {model_name} 下载完成!")
                print("🚀 现在可以启动语音助手了:")
                print("   python voice_api_server_optimized.py")
            else:
                print(f"\n❌ 模型 {model_name} 下载失败")
        else:
            print("👋 下载已取消")
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()