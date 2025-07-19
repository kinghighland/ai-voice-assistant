# 🏗️ 系统设计文档

## 项目概述

### 设计目标
设计一个高性能、易用、可扩展的AI语音助手系统，为Open WebUI提供智能语音交互能力。

### 设计原则
- **模块化**: 组件解耦，便于维护和扩展
- **高性能**: 充分利用GPU加速，优化响应时间
- **易用性**: 简化部署和使用流程
- **可靠性**: 异常处理和降级方案
- **安全性**: 本地处理，保护用户隐私

## 🏛️ 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户层                                │
├─────────────────────────────────────────────────────────────┤
│  浏览器 (Chrome/Firefox/Edge)                               │
│  ├── Open WebUI (http://localhost:8888)                    │
│  └── 语音助手前端脚本 (force_right_button.js)               │
├─────────────────────────────────────────────────────────────┤
│                        网络层                                │
├─────────────────────────────────────────────────────────────┤
│  HTTP/WebSocket 通信                                        │
│  ├── CORS 跨域支持                                          │
│  └── RESTful API 接口                                       │
├─────────────────────────────────────────────────────────────┤
│                        应用层                                │
├─────────────────────────────────────────────────────────────┤
│  语音API服务 (FastAPI)                                      │
│  ├── 语音转录模块                                           │
│  ├── 智能指令识别模块                                        │
│  ├── 系统指令执行模块                                        │
│  └── AI对话模块                                             │
├─────────────────────────────────────────────────────────────┤
│                        AI模型层                              │
├─────────────────────────────────────────────────────────────┤
│  Whisper 语音识别模型                                       │
│  ├── large-v3 (最佳质量)                                    │
│  ├── medium (平衡选择)                                      │
│  └── base (快速启动)                                        │
├─────────────────────────────────────────────────────────────┤
│                        系统层                                │
├─────────────────────────────────────────────────────────────┤
│  操作系统接口                                               │
│  ├── 应用程序启动                                           │
│  ├── 网站访问                                               │
│  └── 系统操作                                               │
└─────────────────────────────────────────────────────────────┘
```

### 组件关系图

```
┌──────────────┐    HTTP     ┌──────────────┐
│   浏览器     │ ◄─────────► │  语音API     │
│   前端脚本   │             │   服务       │
└──────────────┘             └──────────────┘
                                     │
                                     ▼
                             ┌──────────────┐
                             │  Whisper     │
                             │   模型       │
                             └──────────────┘
                                     │
                                     ▼
                             ┌──────────────┐
                             │  系统指令    │
                             │   执行器     │
                             └──────────────┘
```

## 🔧 核心模块设计

### 1. 语音转录模块

#### 1.1 模块职责
- 接收音频文件
- 调用Whisper模型进行转录
- 优化中文识别准确性
- 返回转录结果

#### 1.2 技术实现
```python
class VoiceTranscriber:
    def __init__(self, model_name="large-v3", device="auto"):
        self.model = whisper.load_model(model_name, device=device)
        self.device = device
    
    def transcribe(self, audio_file):
        # 优化的转录参数
        result = self.model.transcribe(
            audio_file,
            language="zh",
            initial_prompt="以下是普通话的转录，请准确识别应用程序名称。",
            temperature=0.0,
            beam_size=5,
            best_of=5,
            fp16=torch.cuda.is_available()
        )
        return self.preprocess_text(result["text"])
    
    def preprocess_text(self, text):
        # 中文识别错误修正
        corrections = {
            "计时版": "记事本",
            "计时器": "计算器",
            "计算机": "计算器"
        }
        for wrong, correct in corrections.items():
            text = text.replace(wrong, correct)
        return text
```

#### 1.3 性能优化
- **GPU加速**: 自动检测CUDA，优先使用GPU
- **模型缓存**: 模型加载后常驻内存
- **参数优化**: 针对中文优化的转录参数
- **错误修正**: 预处理常见识别错误

### 2. 智能指令识别模块

#### 2.1 模块职责
- 分析转录文本
- 识别指令类型和目标
- 区分指令和普通对话
- 返回识别结果

#### 2.2 指令分类体系
```python
COMMAND_PATTERNS = {
    "应用程序": {
        "keywords": ["打开", "启动", "运行", "开启"],
        "targets": {
            "记事本": ["记事本", "notepad", "文本编辑器"],
            "计算器": ["计算器", "calculator", "计时器", "计算机"],
            # ... 更多应用
        }
    },
    "网站": {
        "keywords": ["打开", "访问", "进入", "去"],
        "targets": {
            "百度": ["百度", "baidu"],
            "谷歌": ["谷歌", "google", "搜索"],
            # ... 更多网站
        }
    },
    "系统操作": {
        "keywords": ["关闭", "退出", "锁屏", "截图"],
        "targets": {
            "锁屏": ["锁屏", "lock", "锁定屏幕"],
            "截图": ["截图", "截屏", "抓图"],
            # ... 更多操作
        }
    }
}
```

#### 2.3 识别算法
```python
def smart_command_detection(text: str) -> tuple[bool, str, str]:
    """智能指令检测"""
    text = preprocess_chinese_text(text.strip())
    text_lower = text.lower()
    
    # 多维度检测：关键词 + 目标 + 上下文
    for cmd_type, config in COMMAND_PATTERNS.items():
        keywords = config["keywords"]
        targets = config["targets"]
        
        # 检查关键词
        has_keyword = any(keyword in text for keyword in keywords)
        
        if has_keyword:
            # 检查目标匹配
            for target_name, target_aliases in targets.items():
                if any(alias in text_lower for alias in target_aliases):
                    return True, cmd_type, target_name
    
    return False, "", ""
```

### 3. 系统指令执行模块

#### 3.1 模块职责
- 执行识别出的系统指令
- 提供执行结果反馈
- 处理执行异常
- 安全控制和权限管理

#### 3.2 执行器设计
```python
class CommandExecutor:
    def __init__(self):
        self.system = platform.system().lower()
        self.safe_commands = self.load_safe_commands()
    
    def execute(self, cmd_type: str, target: str) -> Optional[str]:
        """执行指令"""
        if not self.is_safe_command(cmd_type, target):
            return "❌ 不安全的指令，拒绝执行"
        
        try:
            if cmd_type == "应用程序":
                return self.launch_application(target)
            elif cmd_type == "网站":
                return self.open_website(target)
            elif cmd_type == "系统操作":
                return self.system_operation(target)
        except Exception as e:
            return f"❌ 执行失败: {str(e)}"
    
    def is_safe_command(self, cmd_type: str, target: str) -> bool:
        """安全检查"""
        return (cmd_type, target) in self.safe_commands
```

#### 3.3 安全机制
- **白名单机制**: 只允许预定义的安全指令
- **权限检查**: 危险操作需要用户确认
- **异常处理**: 执行失败时提供友好提示
- **日志记录**: 记录所有指令执行情况

### 4. WebUI集成模块

#### 4.1 前端脚本设计
```javascript
class VoiceAssistant {
    constructor() {
        this.apiUrl = 'http://localhost:8889';
        this.isRecording = false;
        this.init();
    }
    
    init() {
        this.createButton();
        this.bindEvents();
        this.testConnection();
    }
    
    async processVoice(audioBlob) {
        // 1. 上传音频进行转录
        const transcribeResult = await this.transcribe(audioBlob);
        
        // 2. 根据后端判断处理方式
        if (transcribeResult.is_command) {
            await this.executeCommand(transcribeResult.transcribed_text);
        } else {
            this.insertToChat(transcribeResult.transcribed_text);
        }
    }
}
```

#### 4.2 集成策略
- **非侵入式**: 通过JavaScript注入，不修改WebUI源码
- **兼容性**: 支持多种浏览器和WebUI版本
- **用户体验**: 直观的按钮设计和状态提示
- **错误处理**: 网络异常和API错误的友好提示

## 📊 数据流设计

### 1. 语音处理流程

```
用户语音输入
      │
      ▼
浏览器录音 (MediaRecorder)
      │
      ▼
音频数据 (Blob)
      │
      ▼
HTTP POST /transcribe
      │
      ▼
Whisper模型转录
      │
      ▼
中文错误修正
      │
      ▼
智能指令识别
      │
      ▼
┌─────────────┬─────────────┐
│   指令模式   │   对话模式   │
▼             ▼
系统指令执行   文本插入聊天框
│             │
▼             ▼
执行结果反馈   用户确认发送
```

### 2. API接口设计

#### 2.1 转录接口
```
POST /transcribe
Content-Type: multipart/form-data

Request:
- audio_file: 音频文件 (WAV/MP3/M4A)

Response:
{
    "success": true,
    "transcribed_text": "打开记事本",
    "language": "zh",
    "is_command": true,
    "command_type": "应用程序",
    "command_target": "记事本",
    "confidence": 0.95
}
```

#### 2.2 指令处理接口
```
POST /process
Content-Type: application/json

Request:
{
    "text": "打开记事本",
    "execute_commands": true
}

Response:
{
    "transcribed_text": "打开记事本",
    "ai_response": "我来帮您打开记事本",
    "command_executed": true,
    "command_result": "✅ 已为您打开记事本",
    "command_type": "应用程序"
}
```

### 3. 数据存储设计

#### 3.1 模型缓存
```
~/.cache/whisper/
├── large-v3.pt      # 3.1GB
├── medium.pt        # 1.5GB
└── base.pt          # 142MB
```

#### 3.2 配置文件
```
.kiro/settings/
├── voice_config.json    # 语音配置
└── command_config.json  # 指令配置
```

#### 3.3 临时文件
```
/tmp/voice_assistant/
├── audio_*.wav         # 临时音频文件 (自动清理)
└── logs/              # 日志文件
```

## 🚀 部署架构

### 1. 本地部署架构

```
┌─────────────────────────────────────────┐
│              用户机器                    │
├─────────────────────────────────────────┤
│  Docker容器                             │
│  ├── Open WebUI (端口8888)              │
│  └── 数据卷挂载                         │
├─────────────────────────────────────────┤
│  Python进程                             │
│  ├── 语音API服务 (端口8889)             │
│  ├── Whisper模型                        │
│  └── 系统指令执行器                      │
├─────────────────────────────────────────┤
│  操作系统                               │
│  ├── CUDA驱动 (可选)                    │
│  ├── 音频设备                           │
│  └── 系统应用程序                       │
└─────────────────────────────────────────┘
```

### 2. 服务启动流程

```
启动脚本 (simple_start.py)
      │
      ▼
环境检查 (GPU/依赖)
      │
      ▼
模型下载/加载
      │
      ▼
API服务启动
      │
      ▼
健康检查
      │
      ▼
服务就绪
```

### 3. 容器化部署

```yaml
# docker-compose.yml
version: '3.8'
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "8888:8080"
    volumes:
      - open-webui:/app/backend/data
      - ./static:/app/backend/static/custom
    
  voice-assistant:
    build: .
    ports:
      - "8889:8889"
    volumes:
      - ~/.cache/whisper:/root/.cache/whisper
    environment:
      - CUDA_VISIBLE_DEVICES=0
```

## 🔒 安全设计

### 1. 数据安全
- **本地处理**: 语音数据不上传云端
- **临时文件**: 音频文件处理后立即删除
- **内存清理**: 敏感数据及时清理
- **传输加密**: HTTPS通信 (生产环境)

### 2. 系统安全
- **指令白名单**: 只允许安全的系统操作
- **权限控制**: 危险操作需要用户确认
- **沙箱执行**: 限制指令执行权限
- **审计日志**: 记录所有指令执行

### 3. 网络安全
- **CORS配置**: 限制跨域访问
- **输入验证**: 防止注入攻击
- **速率限制**: 防止API滥用
- **错误处理**: 不泄露敏感信息

## 📈 性能优化

### 1. 模型优化
- **GPU加速**: CUDA并行计算
- **模型量化**: FP16精度减少内存
- **批处理**: 支持多音频并行处理
- **模型缓存**: 避免重复加载

### 2. 网络优化
- **连接池**: 复用HTTP连接
- **压缩传输**: Gzip压缩响应
- **缓存策略**: 静态资源缓存
- **异步处理**: 非阻塞IO操作

### 3. 系统优化
- **内存管理**: 及时释放不用的资源
- **进程优化**: 合理的进程和线程配置
- **磁盘IO**: 优化文件读写操作
- **监控告警**: 实时性能监控

## 🧪 测试策略

### 1. 单元测试
- 语音转录模块测试
- 指令识别模块测试
- 系统执行模块测试
- API接口测试

### 2. 集成测试
- 端到端语音处理流程
- WebUI集成测试
- 多浏览器兼容性测试
- 异常场景测试

### 3. 性能测试
- 并发用户测试
- 长时间运行测试
- 资源使用监控
- 响应时间测试

### 4. 用户测试
- 可用性测试
- 用户体验测试
- 多语言环境测试
- 不同硬件配置测试

## 📝 维护和监控

### 1. 日志系统
```python
# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('voice_assistant.log'),
        logging.StreamHandler()
    ]
)
```

### 2. 健康检查
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "whisper_loaded": whisper_model is not None,
        "device": "GPU" if torch.cuda.is_available() else "CPU",
        "timestamp": datetime.now().isoformat()
    }
```

### 3. 性能监控
- CPU/内存使用率
- GPU使用率 (如果有)
- API响应时间
- 错误率统计

### 4. 自动化运维
- 服务自动重启
- 日志轮转
- 模型更新
- 配置热更新

---

*本设计文档将随着项目发展持续更新和完善*