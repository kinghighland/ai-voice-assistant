#!/usr/bin/env python3
"""
GPU内存优化版语音助手启动器
- 支持ModelScope快速下载
- 优先使用turbo模型节省显存
- GPU内存管理优化
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_dependencies():
    """检查依赖"""
    print("🔍 检查系统依赖...")
    
    # 检查基础依赖
    required_packages = ['fastapi', 'uvicorn', 'whisper', 'torch', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 基础依赖检查通过")
    return True

def check_gpu_status():
    """检查GPU状态"""
    print("🔍 检查GPU状态...")
    
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"🎮 检测到GPU: {gpu_name}")
            print(f"💾 GPU内存: {gpu_memory:.1f} GB")
            
            # 检查可用内存
            torch.cuda.empty_cache()
            allocated = torch.cuda.memory_allocated() / 1024**3
            reserved = torch.cuda.memory_reserved() / 1024**3
            free = gpu_memory - reserved
            
            print(f"📊 内存状态: 已用 {allocated:.1f}GB, 已预留 {reserved:.1f}GB, 可用 {free:.1f}GB")
            
            if free < 2.0:
                print("⚠️ GPU内存可能不足，建议使用turbo模型")
            
            return True, gpu_memory
        else:
            print("💻 未检测到CUDA GPU，将使用CPU模式")
            return False, 0
    except Exception as e:
        print(f"⚠️ GPU检查失败: {e}")
        return False, 0

def check_whisper_models():
    """检查Whisper模型"""
    print("🔍 检查Whisper模型...")
    
    cache_dir = Path.home() / ".cache" / "whisper"
    models = {
        "large-v3-turbo": "推荐: 显存占用少，速度快",
        "large-v3": "最佳质量，显存占用大",
        "medium": "平衡选择",
        "base": "轻量级"
    }
    
    available_models = []
    for model_name, desc in models.items():
        model_file = cache_dir / f"{model_name}.pt"
        if model_file.exists():
            size_gb = model_file.stat().st_size / 1024**3
            print(f"✅ {model_name}: {desc} ({size_gb:.1f}GB)")
            available_models.append(model_name)
        else:
            print(f"❌ {model_name}: {desc} (未下载)")
    
    return available_models

def suggest_model_download(has_gpu, gpu_memory):
    """建议模型下载"""
    print("\n💡 模型下载建议:")
    
    if has_gpu and gpu_memory >= 8:
        print("🎯 推荐: large-v3-turbo (最佳平衡)")
        print("   - 显存占用: ~1.5GB")
        print("   - 识别质量: 优秀")
        print("   - 为其他模型预留充足内存")
        recommended = "large-v3-turbo"
    elif has_gpu and gpu_memory >= 4:
        print("🎯 推荐: medium (适中选择)")
        print("   - 显存占用: ~1GB")
        print("   - 识别质量: 良好")
        recommended = "medium"
    else:
        print("🎯 推荐: base (轻量级)")
        print("   - 内存占用: ~300MB")
        print("   - 识别质量: 基础")
        recommended = "base"
    
    print(f"\n下载方式:")
    print(f"1. ModelScope快速下载: python download_whisper_modelscope.py")
    print(f"2. 官方下载: 启动服务时自动下载")
    
    return recommended

def start_voice_service():
    """启动语音服务"""
    print("\n🚀 启动GPU内存优化版语音助手...")
    print("💡 特性:")
    print("   - 优先使用turbo模型节省显存")
    print("   - GPU内存管理优化")
    print("   - 优先执行指令，避免GPU冲突")
    print("   - 支持与其他AI模型共存")
    
    try:
        # 启动优化版服务
        process = subprocess.Popen([
            sys.executable, 
            "voice_api_server.py"
        ])
        
        print("\n⏳ 服务启动中...")
        print("📱 启动完成后可在浏览器中使用语音功能")
        print("🛑 按 Ctrl+C 停止服务")
        print()
        
        # 等待进程
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务...")
        try:
            process.terminate()
            time.sleep(2)
            if process.poll() is None:
                process.kill()
        except:
            pass
        print("✅ 服务已停止")
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def main():
    """主函数"""
    print("🎤 GPU内存优化版AI语音助手启动器")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查GPU状态
    has_gpu, gpu_memory = check_gpu_status()
    
    # 检查模型
    print()
    available_models = check_whisper_models()
    
    if not available_models:
        print("\n❌ 未找到任何Whisper模型")
        recommended = suggest_model_download(has_gpu, gpu_memory)
        
        response = input(f"\n是否使用ModelScope快速下载 {recommended} 模型? (Y/n): ").strip().lower()
        if response in ['', 'y', 'yes']:
            print("🚀 启动ModelScope下载...")
            try:
                subprocess.run([sys.executable, "download_whisper_modelscope.py"], check=True)
            except subprocess.CalledProcessError:
                print("❌ ModelScope下载失败，将使用官方下载")
        else:
            print("💡 将在启动时自动下载模型")
    else:
        print(f"\n✅ 检测到 {len(available_models)} 个可用模型")
        if "large-v3-turbo" in available_models:
            print("🎯 将优先使用 large-v3-turbo 模型")
        elif available_models:
            print(f"🎯 将使用 {available_models[0]} 模型")
    
    # GPU内存优化提示
    if has_gpu:
        print(f"\n🔧 GPU内存优化:")
        print(f"   - Whisper模型将占用70%GPU内存")
        print(f"   - 为其他AI模型预留30%内存")
        print(f"   - 语音指令优先执行，避免模型冲突")
    
    # 启动确认
    print(f"\n" + "=" * 50)
    response = input("是否开始启动服务? (Y/n): ").strip().lower()
    if response in ['', 'y', 'yes']:
        start_voice_service()
    else:
        print("👋 启动已取消")

if __name__ == "__main__":
    main()