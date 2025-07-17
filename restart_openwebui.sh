#!/bin/bash
# 重启Open WebUI并挂载语音插件

echo "停止现有的Open WebUI容器..."
docker stop webui
docker rm webui

echo "启动新的Open WebUI容器并挂载语音插件..."
docker run -d \
  --name webui \
  -p 8888:8080 \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  -e WEBUI_SECRET_KEY=your-secret-key-here \
  -v open-webui:/app/backend/data \
  -v "$(pwd)/voice_assistant_plugin.js:/app/static/js/voice_assistant_plugin.js" \
  --add-host=host.docker.internal:host-gateway \
  --restart unless-stopped \
  ghcr.io/open-webui/open-webui:main

echo "Open WebUI已重启，语音插件已挂载"
echo "访问地址: http://localhost:8888"