# 🎤 AI语音助手 + Open WebUI集成

一个功能强大的中文语音助手，集成了Whisper语音识别、Ollama大语言模型和Open WebUI界面，支持语音控制和智能命令执行。

## ✨ 主要功能

- 🎙️ **高质量中文语音识别** - 基于OpenAI Whisper medium模型
- 🤖 **智能AI对话** - 集成Ollama多种大语言模型
- ⚡ **系统命令执行** - 语音控制打开网站、启动应用
- 🌐 **Web界面集成** - 美观的Open WebUI界面
- 📱 **跨平台支持** - 支持桌面和移动设备
- 🐳 **Docker部署** - 一键启动所有服务

## 🚀 快速开始

### 前置要求
- Docker & Docker Compose
- Ollama (已安装并运行)
- 现代浏览器 (支持Web Audio API)

### 1. 克隆项目
```bash
git clone https://github.com/kinghighland/ai-voice-assistant.git
cd ai-voice-assistant
```

### 2. 启动Ollama服务
```bash
# 启动Ollama
ollama serve

# 安装模型 (选择一个或多个)
ollama pull minicpm-v
ollama pull qwen3:14b
ollama pull deepseek-r1:14b
```

### 3. 启动集成服务
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 4. 访问服务
- **Open WebUI**: http://localhost:3000
- **语音API**: http://localhost:8001
- **API文档**: http://localhost:8001/docs

## 🎯 使用方法

### Web界面使用
1. 访问 http://localhost:3000
2. 在右下角找到绿色的🎤语音按钮
3. **按住按钮开始录音，松开停止**
4. 语音会自动转录并发送给AI

### 支持的语音命令

#### 🌐 网站访问
- "打开知乎网站" → 打开 https://www.zhihu.com
- "访问百度网页" → 打开百度首页
- "进入B站" → 打开Bilibili
- "打开GitHub" → 打开GitHub

#### 💻 应用启动
- "打开记事本" → 启动Notepad
- "启动计算器" → 打开计算器
- "打开画图" → 启动画图工具
- "打开文件管理器" → 启动资源管理器

#### 🔍 系统搜索
- "搜索天气预报" → 打开Windows搜索

#### 💬 智能对话
- "现在几点了？"
- "今天天气怎么样？"
- "帮我写一段代码"
- 任何问题都会得到AI回复

## 🛠️ 项目结构

```
ai-voice-assistant/
├── voice_assistant.py          # 独立语音助手 (按键控制)
├── voice_api_server.py         # FastAPI后端服务
├── voice_assistant_plugin.js   # Open WebUI前端插件
├── docker-compose.yml          # Docker编排配置
├── Dockerfile                  # 语音API容器配置
├── requirements.txt            # Python依赖
├── change_port.py             # 端口修改工具
├── setup_voice_webui.md       # 详细部署指南
└── test/                      # 测试文件
    ├── test-api.py           # API测试脚本
    ├── test-tts.py           # 语音合成测试
    └── test-whisper.py       # 语音识别测试
```

## ⚙️ 配置选项

### 修改端口
```bash
# 将API端口从8001改为8002
python change_port.py 8001 8002

# 重新构建服务
docker-compose build
docker-compose up -d
```

### 自定义Whisper模型
编辑 `voice_api_server.py`:
```python
# 可选: tiny, base, small, medium, large
whisper_model = whisper.load_model("large")
```

### 添加更多网站支持
编辑 `voice_api_server.py` 中的 `execute_system_command` 函数。

## 🐛 故障排除

### 常见问题

**语音按钮不显示**
- 检查浏览器是否支持Web Audio API
- 确认在HTTPS或localhost环境下访问

**录音权限被拒绝**
- 在浏览器设置中允许麦克风权限
- 检查系统麦克风设置

**AI不回复**
```bash
# 检查Ollama服务
ollama serve
ollama list

# 查看API日志
docker-compose logs voice-assistant-api
```

**命令不执行**
- 确认语音识别准确性
- Windows系统命令需要在主机上运行

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务
docker-compose logs -f voice-assistant-api
```

## 🔧 开发

### 本地开发
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 启动API服务
python voice_api_server.py

# 运行独立语音助手
python voice_assistant.py
```

### API测试
```bash
# 测试API功能
python test/test-api.py

# 测试语音识别
python test/test-whisper.py

# 测试语音合成
python test/test-tts.py
```

## 📝 技术栈

- **语音识别**: OpenAI Whisper
- **大语言模型**: Ollama (支持多种模型)
- **后端框架**: FastAPI
- **前端界面**: Open WebUI + 自定义JavaScript插件
- **容器化**: Docker & Docker Compose
- **语音合成**: pyttsx3

## 🤝 贡献

欢迎提交Issue和Pull Request！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [OpenAI Whisper](https://github.com/openai/whisper) - 语音识别
- [Ollama](https://ollama.ai/) - 本地大语言模型
- [Open WebUI](https://github.com/open-webui/open-webui) - Web界面
- [FastAPI](https://fastapi.tiangolo.com/) - 后端框架

## 📞 联系

如果你有任何问题或建议，欢迎：
- 提交 [Issue](https://github.com/kinghighland/ai-voice-assistant/issues)
- 发起 [Discussion](https://github.com/kinghighland/ai-voice-assistant/discussions)

---

⭐ 如果这个项目对你有帮助，请给个Star支持一下！