#!/usr/bin/env python3
"""
GPU状态检测脚本
"""

import subprocess
import sys

def test_nvidia_driver():
    """测试NVIDIA驱动"""
    print("🔍 检测NVIDIA驱动...")
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ NVIDIA驱动正常")
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Driver Version' in line:
                    print(f"📋 {line.strip()}")
                elif 'CUDA Version' in line:
                    print(f"📋 {line.strip()}")
            return True
        else:
            print("❌ NVIDIA驱动异常")
            print(result.stderr)
            return False
    except FileNotFoundError:
        print("❌ 未找到nvidia-smi命令")
        print("💡 可能原因: 未安装NVIDIA驱动或不在PATH中")
        return False
    except Exception as e:
        print(f"❌ 检测失败: {e}")
        return False

def test_pytorch():
    """测试PyTorch GPU支持"""
    print("\n🔍 检测PyTorch GPU支持...")
    try:
        import torch
        print(f"✅ PyTorch版本: {torch.__version__}")
        
        # 检查CUDA编译支持
        if torch.version.cuda:
            print(f"✅ CUDA编译版本: {torch.version.cuda}")
        else:
            print("❌ PyTorch未编译CUDA支持")
            return False
        
        # 检查CUDA运行时可用性
        if torch.cuda.is_available():
            print("✅ CUDA运行时可用")
            print(f"🔢 GPU数量: {torch.cuda.device_count()}")
            
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                print(f"🎮 GPU {i}: {props.name}")
                print(f"💾 显存: {props.total_memory / 1024**3:.1f} GB")
                print(f"🔧 计算能力: {props.major}.{props.minor}")
            
            return True
        else:
            print("❌ CUDA运行时不可用")
            return False
            
    except ImportError:
        print("❌ 未安装PyTorch")
        return False
    except Exception as e:
        print(f"❌ 检测失败: {e}")
        return False

def test_whisper_gpu():
    """测试Whisper GPU支持"""
    print("\n🔍 测试Whisper GPU加载...")
    try:
        import whisper
        import torch
        
        if not torch.cuda.is_available():
            print("⚠️ CUDA不可用，跳过GPU测试")
            return False
        
        print("📦 尝试加载小模型到GPU...")
        device = "cuda"
        model = whisper.load_model("tiny", device=device)
        print(f"✅ 成功加载Whisper模型到GPU")
        
        # 测试GPU内存使用
        if torch.cuda.is_available():
            memory_allocated = torch.cuda.memory_allocated() / 1024**2
            memory_reserved = torch.cuda.memory_reserved() / 1024**2
            print(f"📊 GPU内存使用: {memory_allocated:.1f} MB (已分配)")
            print(f"📊 GPU内存预留: {memory_reserved:.1f} MB (已预留)")
        
        return True
        
    except Exception as e:
        print(f"❌ Whisper GPU测试失败: {e}")
        return False

def provide_solutions():
    """提供解决方案"""
    print("\n" + "="*50)
    print("💡 GPU问题解决方案")
    print("="*50)
    
    print("\n1️⃣ 如果NVIDIA驱动有问题:")
    print("   - 访问 https://www.nvidia.com/drivers")
    print("   - 下载并安装最新驱动")
    print("   - 重启电脑")
    
    print("\n2️⃣ 如果PyTorch没有CUDA支持:")
    print("   - 卸载现有PyTorch:")
    print("     pip uninstall torch torchvision torchaudio")
    print("   - 安装CUDA版本:")
    print("     pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    
    print("\n3️⃣ 如果CUDA版本不匹配:")
    print("   - 检查NVIDIA驱动支持的CUDA版本")
    print("   - 安装对应版本的PyTorch")
    print("   - 参考: https://pytorch.org/get-started/locally/")
    
    print("\n4️⃣ 如果仍有问题:")
    print("   - 检查Windows版本是否支持CUDA")
    print("   - 确认GPU型号支持CUDA")
    print("   - 考虑使用CPU模式 (性能较慢但功能完整)")

def main():
    """主函数"""
    print("🔧 GPU状态诊断工具")
    print("="*50)
    
    # 测试NVIDIA驱动
    nvidia_ok = test_nvidia_driver()
    
    # 测试PyTorch
    pytorch_ok = test_pytorch()
    
    # 测试Whisper
    whisper_ok = test_whisper_gpu() if pytorch_ok else False
    
    # 总结
    print("\n" + "="*50)
    print("📋 诊断结果总结")
    print("="*50)
    print(f"NVIDIA驱动: {'✅ 正常' if nvidia_ok else '❌ 异常'}")
    print(f"PyTorch GPU: {'✅ 正常' if pytorch_ok else '❌ 异常'}")
    print(f"Whisper GPU: {'✅ 正常' if whisper_ok else '❌ 异常'}")
    
    if nvidia_ok and pytorch_ok and whisper_ok:
        print("\n🎉 GPU环境完全正常！可以使用GPU加速")
    elif nvidia_ok and pytorch_ok:
        print("\n⚠️ GPU基础环境正常，但Whisper GPU加载有问题")
    elif nvidia_ok:
        print("\n⚠️ NVIDIA驱动正常，但PyTorch没有GPU支持")
    else:
        print("\n❌ GPU环境有问题，建议使用CPU模式")
    
    # 提供解决方案
    if not (nvidia_ok and pytorch_ok and whisper_ok):
        provide_solutions()

if __name__ == "__main__":
    main()