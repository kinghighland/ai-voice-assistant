FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    portaudio19-dev \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖 (包括ModelScope)
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY voice_api_server.py .
COPY config.py .
COPY download_whisper_modelscope.py .
COPY test_gpu.py .
COPY AI_button_browser_plugin.js ./static/

# 创建缓存目录
RUN mkdir -p /root/.cache/whisper

# 暴露端口
EXPOSE 8889

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=0

# 启动命令
CMD ["python", "voice_api_server.py"]