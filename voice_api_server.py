#!/usr/bin/env python3
"""
优化版语音助手API服务器 - GPU内存优化版
- 支持Whisper-large-v3-turbo模型，显存占用更少
- 优化GPU内存管理，支持多模型共存
- 优先执行指令，跳过AI回复避免GPU冲突
- 集成ModelScope快速下载
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import whisper
import requests
import os
import platform
import subprocess
import tempfile
import uvicorn
from pydantic import BaseModel
from typing import Optional, List
import logging
import torch
import re
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI应用将在后面定义，避免重复

# 全局变量
whisper_model = None
OLLAMA_API_BASE = "http://localhost:11434/api"

class VoiceRequest(BaseModel):
    text: str
    execute_commands: bool = True

class VoiceResponse(BaseModel):
    transcribed_text: str
    ai_response: str
    command_executed: bool = False
    command_result: Optional[str] = None
    command_type: Optional[str] = None

# 扩展的指令识别词典
COMMAND_PATTERNS = {
    "应用程序": {
        "keywords": ["打开", "启动", "运行", "开启"],
        "targets": {
            "记事本": ["记事本", "notepad", "文本编辑器"],
            "计算器": ["计算器", "calculator", "计时器", "计时版", "计算机"],
            "画图": ["画图", "画板", "绘图", "paint"],
            "文件管理器": ["文件管理器", "资源管理器", "文件夹", "explorer"],
            "浏览器": ["浏览器", "browser", "网页", "上网"],
            "任务管理器": ["任务管理器", "进程管理", "task manager"],
            "控制面板": ["控制面板", "设置", "系统设置"],
            "命令提示符": ["命令提示符", "cmd", "终端", "控制台"],
            "PowerShell": ["powershell", "ps", "power shell"]
        }
    },
    "网站": {
        "keywords": ["打开", "访问", "进入", "去", "看看"],
        "targets": {
            "百度": ["百度", "baidu"],
            "谷歌": ["谷歌", "google", "搜索"],
            "知乎": ["知乎", "zhihu"],
            "微博": ["微博", "weibo"],
            "哔哩哔哩": ["哔哩哔哩", "bilibili", "b站", "B站"],
            "淘宝": ["淘宝", "taobao", "购物"],
            "京东": ["京东", "jd", "商城"],
            "GitHub": ["github", "代码", "开源"],
            "YouTube": ["youtube", "油管", "视频"],
            "网易云音乐": ["网易云", "音乐", "歌曲"]
        }
    },
    "系统操作": {
        "keywords": ["关闭", "退出", "结束", "停止", "重启", "关机"],
        "targets": {
            "关机": ["关机", "shutdown", "关闭电脑"],
            "重启": ["重启", "restart", "重新启动"],
            "注销": ["注销", "logout", "登出"],
            "锁屏": ["锁屏", "lock", "锁定屏幕"],
            "休眠": ["休眠", "sleep", "待机"]
        }
    },
    "文件操作": {
        "keywords": ["新建", "创建", "删除", "复制", "移动"],
        "targets": {
            "新建文件夹": ["新建文件夹", "创建文件夹", "建文件夹"],
            "新建文件": ["新建文件", "创建文件", "建文件"],
            "截图": ["截图", "截屏", "抓图", "screenshot"]
        }
    }
}

from contextlib import asynccontextmanager



@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    global whisper_model
    logger.info("🚀 正在启动优化版语音助手API服务...")
    
    logger.info("📥 开始加载Whisper模型（首次运行可能需要下载模型文件）...")
    
    # 导入必要的模块
    import torch
    import whisper
    import gc
    
    # 检查GPU可用性
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"🔧 使用设备: {device}")
    
    if device == "cuda":
        logger.info(f"🎮 GPU信息: {torch.cuda.get_device_name(0)}")
        logger.info(f"💾 GPU内存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    # 优先使用turbo模型以节省GPU内存
    model_priority = ["large-v3-turbo", "large-v3", "large-v2", "medium", "base"]
    
    for i, model_name in enumerate(model_priority):
        try:
            logger.info(f"📦 尝试加载 Whisper {model_name} 模型... ({i+1}/{len(model_priority)})")
            
            # 提供模型大小信息
            model_sizes = {
                "large-v3-turbo": "1.5GB",  # turbo版本显存占用更少
                "large-v3": "3.1GB",
                "large-v2": "3.1GB", 
                "large": "3.1GB",
                "medium": "1.5GB",
                "base": "290MB"
            }
            
            if model_name in model_sizes:
                logger.info(f"📊 模型大小: {model_sizes[model_name]}")
                if i == 0:
                    logger.info("💡 提示: 首次下载可能需要几分钟，模型会缓存到本地")
                    logger.info("🌐 使用官方源下载 (可能较慢，请耐心等待)")
            
            # 显示加载状态
            logger.info("⏳ 正在加载模型，请稍候...")
            if i == 0:
                logger.info("💡 首次下载可能需要几分钟，请耐心等待...")
                logger.info("🌐 如果下载很慢，可以按 Ctrl+C 中断，稍后重试")
            
            # 清理GPU内存
            if device == "cuda":
                torch.cuda.empty_cache()
                gc.collect()
            
            # 特殊处理turbo模型 - 直接从文件加载
            if model_name == "large-v3-turbo":
                turbo_path = Path.home() / ".cache" / "whisper" / "large-v3-turbo.pt"
                if turbo_path.exists():
                    logger.info(f"🎯 直接加载turbo模型文件: {turbo_path}")
                    whisper_model = whisper.load_model(str(turbo_path), device=device)
                else:
                    logger.warning(f"⚠️ turbo模型文件不存在: {turbo_path}")
                    continue
            else:
                # 加载官方模型
                whisper_model = whisper.load_model(
                    model_name, 
                    device=device,
                    in_memory=True  # 保持在内存中以提高性能
                )
            
            # 如果是GPU模式，设置内存分配策略
            if device == "cuda":
                # 设置更保守的内存分配，为其他模型预留更多空间
                torch.cuda.set_per_process_memory_fraction(0.5)  # 只使用50%GPU内存
                logger.info("🔧 GPU内存分配: 50% (为其他AI模型预留50%)")
            
            logger.info(f"✅ 成功加载 Whisper {model_name} 模型到 {device}")
            
            # 显示模型信息
            if hasattr(whisper_model, 'dims'):
                logger.info(f"🔧 模型参数: {whisper_model.dims}")
            
            break
        except Exception as e:
            logger.warning(f"❌ 无法加载 {model_name} 模型: {e}")
            if i < len(model_priority) - 1:
                logger.info(f"🔄 尝试加载下一个模型...")
            continue
    
    if whisper_model is None:
        logger.error("💥 所有模型加载失败！")
        raise RuntimeError("无法加载任何Whisper模型")
    
    logger.info("🎉 语音助手API服务启动完成！")
    logger.info(f"🌐 服务地址: http://localhost:8889")
    logger.info(f"📚 API文档: http://localhost:8889/docs")
    
    yield  # 应用运行期间
    
    # 关闭时执行
    logger.info("🛑 正在关闭语音助手API服务...")

# 重新创建FastAPI应用，正确设置lifespan参数
app = FastAPI(
    title="优化版语音助手API", 
    version="2.0.0",
    description="支持GPU加速的中文语音识别和智能指令执行",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "优化版语音助手API服务正在运行", "status": "healthy"}

@app.get("/health")
async def health_check():
    """健康检查接口"""
    device_info = "GPU" if torch.cuda.is_available() else "CPU"
    return {
        "status": "healthy", 
        "whisper_loaded": whisper_model is not None,
        "device": device_info,
        "model_info": str(whisper_model) if whisper_model else None
    }

def preprocess_chinese_text(text: str) -> str:
    """预处理中文文本，修正常见识别错误"""
    corrections = {
        # 常见的中文识别错误修正
        "计时版": "记事本",
        "计时器": "计算器", 
        "计算机": "计算器",
        "记事版": "记事本",
        "文件管理": "文件管理器",
        "资源管理": "文件管理器",
        "任务管理": "任务管理器",
        "控制版": "控制面板",
        "哔哩哔哩": "bilibili",
        "B站": "bilibili",
        "b站": "bilibili",
        "网易云": "网易云音乐",
        "谷歌": "google",
        "百度一下": "百度",
        # 新增的常见错误
        "大开": "打开",
        "打开浏览器访问": "打开",
        "浏览器访问": "打开",
        "访问知乎网站": "知乎",
        "知乎网站": "知乎",
        "百度网站": "百度",
        "谷歌网站": "谷歌",
        "微博网站": "微博",
        "计算机器": "计算器",
        "记事簿": "记事本",
        "文本编辑": "记事本"
    }
    
    corrected_text = text
    for wrong, correct in corrections.items():
        corrected_text = corrected_text.replace(wrong, correct)
    
    return corrected_text

def smart_command_detection(text: str) -> tuple[bool, str, str]:
    """智能指令检测 - 返回(是否为指令, 指令类型, 目标)"""
    text = preprocess_chinese_text(text.strip())
    text_lower = text.lower()
    
    # 检查每种指令类型
    for cmd_type, config in COMMAND_PATTERNS.items():
        keywords = config["keywords"]
        targets = config["targets"]
        
        # 检查是否包含关键词
        has_keyword = any(keyword in text for keyword in keywords)
        
        if has_keyword:
            # 检查目标
            for target_name, target_aliases in targets.items():
                if any(alias in text_lower for alias in target_aliases):
                    return True, cmd_type, target_name
    
    # 特殊情况：直接说应用名称
    for cmd_type, config in COMMAND_PATTERNS.items():
        if cmd_type in ["应用程序", "网站"]:
            for target_name, target_aliases in config["targets"].items():
                if any(alias in text_lower for alias in target_aliases):
                    # 如果文本很短且主要是应用名称，认为是指令
                    if len(text.strip()) <= 10:
                        return True, cmd_type, target_name
    
    return False, "", ""

@app.post("/transcribe", response_model=dict)
async def transcribe_audio(audio_file: UploadFile = File(...)):
    """优化的语音转文字接口"""
    if not whisper_model:
        raise HTTPException(status_code=500, detail="Whisper模型未加载")
    
    try:
        # 保存上传的音频文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # 优化的Whisper转录参数
        logger.info("开始转录音频...")
        result = whisper_model.transcribe(
            temp_file_path,
            language="zh",  # 强制中文
            initial_prompt="以下是普通话的转录，请准确识别应用程序名称如记事本、计算器等。",
            temperature=0.0,  # 降低随机性
            beam_size=5,      # 增加beam search
            best_of=5,        # 多次尝试取最佳
            fp16=torch.cuda.is_available(),  # GPU时使用fp16加速
            condition_on_previous_text=False,  # 不依赖前文
            no_speech_threshold=0.6,
            logprob_threshold=-1.0,
            compression_ratio_threshold=2.4
        )
        
        # 清理临时文件
        os.unlink(temp_file_path)
        
        # 预处理转录结果
        transcribed_text = preprocess_chinese_text(result["text"].strip())
        logger.info(f"转录结果: {transcribed_text}")
        
        # 智能指令检测
        is_command, cmd_type, target = smart_command_detection(transcribed_text)
        
        return {
            "success": True,
            "transcribed_text": transcribed_text,
            "language": result.get("language", "zh"),
            "is_command": is_command,
            "command_type": cmd_type,
            "command_target": target,
            "confidence": result.get("avg_logprob", 0)
        }
        
    except Exception as e:
        logger.error(f"转录错误: {str(e)}")
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"转录失败: {str(e)}")

def execute_enhanced_command(cmd_type: str, target: str, original_text: str) -> Optional[str]:
    """执行增强的系统命令"""
    system = platform.system().lower()
    
    try:
        if cmd_type == "应用程序":
            if system == 'windows':
                commands = {
                    "记事本": "notepad",
                    "计算器": "calc", 
                    "画图": "mspaint",
                    "文件管理器": "explorer",
                    "浏览器": "start msedge",
                    "任务管理器": "taskmgr",
                    "控制面板": "control",
                    "命令提示符": "cmd",
                    "PowerShell": "powershell"
                }
                
                if target in commands:
                    subprocess.run(commands[target], shell=True)
                    return f"✅ 已为您打开{target}"
        
        elif cmd_type == "网站":
            urls = {
                "百度": "https://www.baidu.com",
                "谷歌": "https://www.google.com", 
                "知乎": "https://www.zhihu.com",
                "微博": "https://weibo.com",
                "哔哩哔哩": "https://www.bilibili.com",
                "淘宝": "https://www.taobao.com",
                "京东": "https://www.jd.com",
                "GitHub": "https://github.com",
                "YouTube": "https://www.youtube.com",
                "网易云音乐": "https://music.163.com"
            }
            
            if target in urls:
                if system == 'windows':
                    os.startfile(urls[target])
                    return f"✅ 已为您打开{target}"
                else:
                    return f"检测到打开网站命令: {urls[target]}"
        
        elif cmd_type == "系统操作":
            if system == 'windows':
                operations = {
                    "关机": "shutdown /s /t 0",
                    "重启": "shutdown /r /t 0", 
                    "注销": "shutdown /l",
                    "锁屏": "rundll32.exe user32.dll,LockWorkStation"
                }
                
                if target in operations:
                    # 危险操作需要确认
                    if target in ["关机", "重启", "注销"]:
                        return f"⚠️ 检测到{target}命令，请手动确认执行"
                    else:
                        subprocess.run(operations[target], shell=True)
                        return f"✅ 已执行{target}"
        
        elif cmd_type == "文件操作":
            if target == "截图" and system == 'windows':
                # 使用Windows截图工具
                subprocess.run("snippingtool", shell=True)
                return "✅ 已打开截图工具"
    
    except Exception as e:
        logger.error(f"执行命令错误: {str(e)}")
        return f"❌ 命令执行失败: {str(e)}"
    
    return None

@app.post("/process", response_model=VoiceResponse)
async def process_voice_command(request: VoiceRequest):
    """处理语音命令接口"""
    try:
        text = request.text
        logger.info(f"处理命令: {text}")
        
        # 智能指令检测
        is_command, cmd_type, target = smart_command_detection(text)
        logger.info(f"指令检测结果: is_command={is_command}, cmd_type={cmd_type}, target={target}")
        
        # 执行系统命令 (优先执行，不依赖AI回复)
        command_executed = False
        command_result = None
        
        if request.execute_commands and is_command:
            logger.info(f"开始执行指令: {cmd_type} - {target}")
            command_result = execute_enhanced_command(cmd_type, target, text)
            if command_result and not command_result.startswith("抱歉"):
                command_executed = True
                logger.info(f"指令执行成功: {command_result}")
            else:
                logger.warning(f"指令执行失败: {command_result}")
        
        # 获取AI回复 (只有非指令才需要AI回复)
        ai_response = "指令已处理" if is_command else "正在处理您的请求..."
        
        # 只有普通对话才调用AI模型，避免GPU内存冲突
        if not is_command:
            try:
                # 为了避免GPU内存冲突，暂时禁用AI回复
                # ai_response = await get_ai_response(text)
                ai_response = "语音指令模式下暂不支持AI对话，请直接在聊天框中输入文字进行AI对话"
            except Exception as e:
                logger.warning(f"AI回复获取失败: {e}")
                ai_response = "抱歉，AI服务暂时不可用"
        
        return VoiceResponse(
            transcribed_text=text,
            ai_response=ai_response,
            command_executed=command_executed,
            command_result=command_result,
            command_type=cmd_type if is_command else None
        )
        
    except Exception as e:
        logger.error(f"处理命令错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

async def get_ai_response(text: str) -> str:
    """获取AI回复"""
    models_to_try = ['minicpm-v:latest', 'qwen3:14b', 'deepseek-r1:14b', 'llama3.2-vision:11b']
    
    for model_name in models_to_try:
        try:
            logger.info(f"尝试模型: {model_name}")
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
                logger.info(f"成功使用模型: {model_name}")
                return ai_response
            else:
                logger.warning(f"模型 {model_name} HTTP错误: {response.status_code}")
                continue
                
        except Exception as e:
            logger.warning(f"模型 {model_name} 失败: {str(e)}")
            continue
    
    return "抱歉，我无法连接到AI模型。请确保Ollama正在运行并且已安装模型。"

if __name__ == "__main__":
    from config import Config
    
    # 打印配置信息
    Config.print_config()
    
    # 使用配置启动服务
    uvicorn.run(app, host=Config.API_HOST, port=Config.API_PORT)