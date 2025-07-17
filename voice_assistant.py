import whisper
import pyttsx3
import pyaudio
import wave
import pyautogui
import subprocess
import ollama
import requests
import os
import platform
import keyboard
import threading
import time

# 初始化
# 使用更大的Whisper模型以提高中文识别准确率
print("正在加载Whisper模型...")
model = whisper.load_model("medium")  # 从base升级到medium，更好的中文支持
engine = pyttsx3.init()

# 设置中文语音
voices = engine.getProperty('voices')
for voice in voices:
    if 'chinese' in voice.name.lower() or 'mandarin' in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break
engine.setProperty('rate', 150)  # 语速调慢一点

def record_audio_with_key_control(filename="input.wav", max_duration=30):
    """按住Enter录音，松开停止的录音函数"""
    chunk = 4096
    format = pyaudio.paInt16
    channels = 1
    rate = 44100
    
    print("🎤 按住Enter键开始录音，松开停止...")
    
    # 等待用户按下Enter键
    while True:
        if keyboard.is_pressed('enter'):
            break
        time.sleep(0.01)
    
    print("🎤 录音中，松开Enter键停止...")
    
    p = pyaudio.PyAudio()
    
    # 选择最佳音频输入设备
    input_device_index = None
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            input_device_index = i
            break
    
    stream = p.open(
        format=format,
        channels=channels,
        rate=rate,
        input=True,
        input_device_index=input_device_index,
        frames_per_buffer=chunk
    )
    
    frames = []
    start_time = time.time()
    
    while keyboard.is_pressed('enter'):
        try:
            data = stream.read(chunk, exception_on_overflow=False)
            frames.append(data)
            
            # 显示录音时长
            elapsed = time.time() - start_time
            print(f"\r🎤 录音中... {elapsed:.1f}秒", end="", flush=True)
            
            # 防止录音时间过长
            if elapsed > max_duration:
                print(f"\n⚠️ 录音时间超过{max_duration}秒，自动停止")
                break
                
        except Exception as e:
            print(f"\n录音错误: {e}")
            break
    
    print("\n✅ 录音完成，正在处理...")
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    if not frames:
        print("❌ 没有录制到音频数据")
        return False
    
    # 保存为高质量WAV文件
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    return True

def process_command(text):
    # 使用Ollama处理命令 (HTTP API approach)
    try:
        print("Testing Ollama connection...")
        
        # Try different models in order of preference (using exact names from your system)
        models_to_try = ['minicpm-v:latest', 'qwen3:14b', 'deepseek-r1:14b', 'llama3.2-vision:11b']
        
        ai_response = ""
        for model_name in models_to_try:
            try:
                print(f"Trying model: {model_name}")
                
                # Use HTTP API directly
                OLLAMA_API_BASE = "http://localhost:11434/api"
                response = requests.post(
                    f"{OLLAMA_API_BASE}/generate",
                    json={
                        "model": model_name,
                        "prompt": f"请用中文回答这个问题: {text}",
                        "stream": False
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result['response'].strip()
                    print(f"Successfully used model: {model_name}")
                    break
                else:
                    print(f"HTTP error {response.status_code} for model {model_name}")
                    continue
                    
            except Exception as model_error:
                print(f"Failed to use model {model_name}: {model_error}")
                continue
        
        if not ai_response:
            ai_response = "抱歉，我无法连接到AI模型。请确保Ollama正在运行并且已安装模型。"
        
        # 控制逻辑部分 - 检查是否包含控制命令
        command_lower = text.lower()
        system = platform.system().lower()
        
        # 检查打开网站的命令
        if any(keyword in text for keyword in ["打开", "访问", "进入"]) and any(site in text for site in ["网站", "网页"]):
            url = ""
            if "知乎" in text:
                url = "https://www.zhihu.com"
            elif "百度" in text:
                url = "https://www.baidu.com"
            elif "谷歌" in text or "google" in command_lower:
                url = "https://www.google.com"
            elif "微博" in text:
                url = "https://weibo.com"
            elif "bilibili" in text or "b站" in text:
                url = "https://www.bilibili.com"
            elif "淘宝" in text:
                url = "https://www.taobao.com"
            elif "京东" in text:
                url = "https://www.jd.com"
            elif "github" in command_lower:
                url = "https://github.com"
            
            if url and system == 'windows':
                try:
                    os.startfile(url)
                    return f"✅ 已为您打开 {url}"
                except:
                    return f"❌ 无法打开网站 {url}"
            elif url:
                return f"正在尝试打开 {url}"
        
        # 检查打开浏览器的命令
        elif any(keyword in command_lower for keyword in ["open browser", "打开浏览器", "开启浏览器"]):
            if system == 'windows':
                try:
                    os.startfile("https://www.google.com")
                    return "✅ 已为您打开浏览器"
                except:
                    return "❌ 无法打开浏览器"
            return "正在尝试打开浏览器"
        
        # 检查搜索命令
        elif any(keyword in command_lower for keyword in ["search", "搜索", "查找"]):
            search_term = ""
            if "search" in command_lower:
                search_term = command_lower.split("search")[-1].strip()
            elif "搜索" in text:
                search_term = text.split("搜索")[-1].strip()
            elif "查找" in text:
                search_term = text.split("查找")[-1].strip()
            
            if search_term and system == 'windows':
                try:
                    pyautogui.hotkey('win', 's')
                    pyautogui.write(search_term)
                    pyautogui.press('enter')
                    return f"✅ 已为您搜索：{search_term}"
                except:
                    return f"❌ 无法执行搜索：{search_term}"
            return f"正在搜索：{search_term}"
        
        # 检查打开应用程序的命令
        elif any(keyword in text for keyword in ["打开", "启动"]) and any(app in text for app in ["记事本", "计算器", "画图", "文件管理器"]):
            if system == 'windows':
                try:
                    if "记事本" in text:
                        subprocess.run("notepad", shell=True)
                        return "✅ 已为您打开记事本"
                    elif "计算器" in text:
                        subprocess.run("calc", shell=True)
                        return "✅ 已为您打开计算器"
                    elif "画图" in text:
                        subprocess.run("mspaint", shell=True)
                        return "✅ 已为您打开画图"
                    elif "文件管理器" in text:
                        subprocess.run("explorer", shell=True)
                        return "✅ 已为您打开文件管理器"
                except:
                    return "❌ 无法打开应用程序"
        
        # 如果没有识别到控制命令，返回AI回答
        return ai_response
        
    except Exception as e:
        print(f"Ollama connection error: {str(e)}")
        return f"Error processing command: {str(e)}"

# 主循环
print("🎙️ 语音助手已启动！")
print("💡 使用方法：按住Enter键录音，松开停止")
print("🚪 按Ctrl+C退出程序")
print("-" * 50)

while True:
    try:
        # 使用新的按键控制录音
        if record_audio_with_key_control():
            # 优化的转录设置，专门针对中文
            print("🔄 正在转录语音...")
            result = model.transcribe(
                "input.wav",
                language="zh",  # 指定中文语言
                initial_prompt="以下是普通话的转录。",  # 中文提示词
                temperature=0.0,  # 降低随机性，提高准确性
                beam_size=5,  # 使用beam search提高质量
                best_of=5,  # 尝试多次取最佳结果
                fp16=False  # 在CPU上禁用FP16
            )
            
            text = result["text"].strip()
            print(f"🗣️ 您说的是: {text}")
            
            if not text:
                print("❌ 没有检测到语音，请重试")
                continue
            
            print("🤖 AI正在思考...")
            response = process_command(text)
            print(f"🤖 AI回复: {response}")
            
            # 语音播报
            engine.say(response)
            engine.runAndWait()
            
            print("-" * 50)
        else:
            print("❌ 录音失败，请重试")
            
    except KeyboardInterrupt:
        print("\n👋 再见！")
        break
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        print("请重试...")