#!/usr/bin/env python3
"""
AI语音助手配置文件
"""

import os
from typing import Optional

class Config:
    """配置类"""
    
    # API服务配置
    API_HOST: str = os.getenv("VOICE_API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("VOICE_API_PORT", "8889"))
    
    # WebUI配置
    WEBUI_PORT: int = int(os.getenv("WEBUI_PORT", "8888"))
    
    # Whisper模型配置
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "large-v3-turbo")
    WHISPER_DEVICE: str = os.getenv("WHISPER_DEVICE", "auto")  # auto, cuda, cpu
    
    # GPU内存配置
    GPU_MEMORY_FRACTION: float = float(os.getenv("GPU_MEMORY_FRACTION", "0.5"))
    
    # Ollama配置
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/api")
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # 安全配置
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    
    @classmethod
    def get_api_url(cls) -> str:
        """获取API完整URL"""
        return f"http://localhost:{cls.API_PORT}"
    
    @classmethod
    def get_webui_url(cls) -> str:
        """获取WebUI完整URL"""
        return f"http://localhost:{cls.WEBUI_PORT}"
    
    @classmethod
    def load_from_env_file(cls, env_file: str = ".env") -> None:
        """从.env文件加载配置"""
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
        except FileNotFoundError:
            pass  # .env文件不存在时忽略
    
    @classmethod
    def print_config(cls) -> None:
        """打印当前配置"""
        print("🔧 当前配置:")
        print(f"   API服务: {cls.get_api_url()}")
        print(f"   WebUI: {cls.get_webui_url()}")
        print(f"   Whisper模型: {cls.WHISPER_MODEL}")
        print(f"   设备: {cls.WHISPER_DEVICE}")
        print(f"   GPU内存分配: {cls.GPU_MEMORY_FRACTION * 100}%")

# 加载配置
Config.load_from_env_file()