#!/usr/bin/env python3
"""
语音助手API服务器 - 为Open WebUI提供语音处理接口
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
from typing import Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="语音助手API", version="1.0.0")

# 添加CORS中间件，允许Open WebUI访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.on_event("startup")
async def startup_event():
    """启动时加载Whisper模型"""
    global whisper_model
    logger.info("正在加载Whisper模型...")
    whisper_model = whisper.load_model("medium")
    logger.info("Whisper模型加载完成")

@app.get("/")
async def root():
    return {"message": "语音助手API服务正在运行", "status": "healthy"}

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "whisper_loaded": whisper_model is not None}

@app.post("/transcribe", response_model=dict)
async def transcribe_audio(audio_file: UploadFile = File(...)):
    """语音转文字接口"""
    if not whisper_model:
        raise HTTPException(status_code=500, detail="Whisper模型未加载")
    
    try:
        # 保存上传的音频文件到临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # 使用Whisper转录
        logger.info("开始转录音频...")
        result = whisper_model.transcribe(
            temp_file_path,
            language="zh",
            initial_prompt="以下是普通话的转录。",
            temperature=0.0,
            beam_size=5,
            best_of=5,
            fp16=False
        )
        
        # 清理临时文件
        os.unlink(temp_file_path)
        
        transcribed_text = result["text"].strip()
        logger.info(f"转录结果: {transcribed_text}")
        
        return {
            "success": True,
            "transcribed_text": transcribed_text,
            "language": result.get("language", "zh")
        }
        
    except Exception as e:
        logger.error(f"转录错误: {str(e)}")
        # 清理临时文件
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"转录失败: {str(e)}")

@app.post("/process", response_model=VoiceResponse)
async def process_voice_command(request: VoiceRequest):
    """处理语音命令接口"""
    try:
        text = request.text
        logger.info(f"处理命令: {text}")
        
        # 获取AI回复
        ai_response = await get_ai_response(text)
        
        # 执行系统命令（如果启用）
        command_executed = False
        command_result = None
        
        if request.execute_commands:
            command_result = execute_system_command(text)
            if command_result and not command_result.startswith("抱歉"):
                command_executed = True
        
        return VoiceResponse(
            transcribed_text=text,
            ai_response=ai_response,
            command_executed=command_executed,
            command_result=command_result
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

def execute_system_command(text: str) -> Optional[str]:
    """执行系统命令"""
    command_lower = text.lower()
    system = platform.system().lower()
    
    try:
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
                os.startfile(url)
                return f"✅ 已为您打开 {url}"
            elif url:
                return f"检测到打开网站命令: {url}"
        
        # 检查打开应用程序的命令
        elif any(keyword in text for keyword in ["打开", "启动"]) and any(app in text for app in ["记事本", "计算器", "画图", "文件管理器"]):
            if system == 'windows':
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
        
    except Exception as e:
        logger.error(f"执行命令错误: {str(e)}")
        return f"❌ 命令执行失败: {str(e)}"
    
    return None

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)