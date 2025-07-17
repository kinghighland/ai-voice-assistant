# 语音助手 + Open WebUI 集成部署指南

## 🚀 快速开始

### 1. 确保Ollama正在运行
```bash
# 启动Ollama服务
ollama serve

# 确认模型已安装
ollama list
```

### 2. 启动集成服务
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 3. 访问服务
- **Open WebUI**: http://localhost:3000
- **语音API**: http://localhost:8001
- **API文档**: http://localhost:8001/docs

## 🎯 功能特性

### 语音交互
- 🎤 **按住录音**: 在Open WebUI界面右下角有语音按钮
- 🗣️ **中文识别**: 优化的中文语音识别
- 🤖 **智能回复**: 集成Ollama模型回复
- ⚡ **命令执行**: 自动执行系统命令

### 支持的语音命令
- **网站访问**: "打开知乎网站"、"访问百度"
- **应用启动**: "打开计算器"、"启动记事本"
- **智能对话**: 任何问题都会得到AI回复

## 🔧 配置说明

### 环境变量
```yaml
# docker-compose.yml 中的关键配置
environment:
  - OLLAMA_BASE_URL=http://host.docker.internal:11434
  - WEBUI_SECRET_KEY=your-secret-key-here
```

### 端口映射
- `3000`: Open WebUI界面
- `8001`: 语音助手API
- `11434`: Ollama服务（主机）

## 🛠️ 自定义配置

### 修改语音模型
编辑 `voice_api_server.py`:
```python
# 更改Whisper模型大小
whisper_model = whisper.load_model("large")  # base/small/medium/large
```

### 添加更多网站支持
编辑 `voice_api_server.py` 中的 `execute_system_command` 函数:
```python
elif "新网站" in text:
    url = "https://example.com"
```

### 自定义UI样式
编辑 `voice_assistant_plugin.js` 中的CSS样式。

## 🐛 故障排除

### 常见问题

1. **语音按钮不显示**
   - 检查浏览器是否支持Web Audio API
   - 确认HTTPS或localhost环境

2. **录音权限被拒绝**
   - 浏览器设置中允许麦克风权限
   - 检查系统麦克风设置

3. **AI不回复**
   - 确认Ollama服务正在运行: `ollama serve`
   - 检查模型是否已安装: `ollama list`
   - 查看API日志: `docker-compose logs voice-assistant-api`

4. **命令不执行**
   - Windows系统命令需要在主机上运行
   - 检查语音识别是否准确

### 日志查看
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f voice-assistant-api
docker-compose logs -f open-webui
```

## 🔄 更新和维护

### 更新服务
```bash
# 停止服务
docker-compose down

# 重新构建
docker-compose build --no-cache

# 启动服务
docker-compose up -d
```

### 备份数据
```bash
# 备份Open WebUI数据
docker cp open-webui:/app/backend/data ./backup/
```

## 🎨 进阶使用

### 集成到现有Open WebUI
如果你已经有运行中的Open WebUI，只需要：

1. 启动语音API服务:
```bash
docker run -d -p 8001:8001 --name voice-api voice-assistant-api
```

2. 在Open WebUI中添加插件:
```html
<script src="http://localhost:8001/voice_assistant_plugin.js"></script>
```

### API直接调用
```bash
# 健康检查
curl http://localhost:8001/health

# 文本处理
curl -X POST "http://localhost:8001/process" \
  -H "Content-Type: application/json" \
  -d '{"text": "打开百度网站", "execute_commands": true}'
```

## 📝 注意事项

1. **安全性**: 生产环境请修改默认密钥和CORS设置
2. **性能**: Whisper模型较大，首次加载需要时间
3. **兼容性**: 需要现代浏览器支持Web Audio API
4. **网络**: 确保容器间网络连通性

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！