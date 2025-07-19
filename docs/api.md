# 📡 API文档

## 概述

AI语音助手提供RESTful API接口，支持语音转录、智能指令处理和系统集成。

### 基础信息
- **Base URL**: `http://localhost:8889`
- **API版本**: v2.0.0
- **数据格式**: JSON
- **字符编码**: UTF-8

### 认证
当前版本无需认证，仅限本地访问。

## 🎤 语音转录接口

### POST /transcribe

将音频文件转录为文字，并进行智能指令识别。

#### 请求参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| audio_file | File | 是 | 音频文件 (WAV/MP3/M4A) |

#### 请求示例

```bash
curl -X POST "http://localhost:8889/transcribe" \
  -H "Content-Type: multipart/form-data" \
  -F "audio_file=@recording.wav"
```

#### 响应格式

```json
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

#### 响应字段说明

| 字段 | 类型 | 描述 |
|------|------|------|
| success | boolean | 转录是否成功 |
| transcribed_text | string | 转录的文字内容 |
| language | string | 识别的语言代码 |
| is_command | boolean | 是否为语音指令 |
| command_type | string | 指令类型 (应用程序/网站/系统操作) |
| command_target | string | 指令目标 |
| confidence | number | 识别置信度 (0-1) |

#### 错误响应

```json
{
  "success": false,
  "error": "转录失败: 音频格式不支持",
  "code": "UNSUPPORTED_FORMAT"
}
```

## 🔧 指令处理接口

### POST /process

处理文本指令，执行系统操作或生成AI回复。

#### 请求参数

```json
{
  "text": "打开记事本",
  "execute_commands": true
}
```

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| text | string | 是 | 要处理的文本 |
| execute_commands | boolean | 否 | 是否执行系统指令 (默认true) |

#### 请求示例

```bash
curl -X POST "http://localhost:8889/process" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "打开记事本",
    "execute_commands": true
  }'
```

#### 响应格式

```json
{
  "transcribed_text": "打开记事本",
  "ai_response": "我来帮您打开记事本",
  "command_executed": true,
  "command_result": "✅ 已为您打开记事本",
  "command_type": "应用程序"
}
```

#### 响应字段说明

| 字段 | 类型 | 描述 |
|------|------|------|
| transcribed_text | string | 原始文本 |
| ai_response | string | AI生成的回复 |
| command_executed | boolean | 指令是否执行成功 |
| command_result | string | 指令执行结果 |
| command_type | string | 指令类型 |

## 🏥 健康检查接口

### GET /health

检查服务健康状态和系统信息。

#### 请求示例

```bash
curl -X GET "http://localhost:8889/health"
```

#### 响应格式

```json
{
  "status": "healthy",
  "whisper_loaded": true,
  "device": "GPU",
  "model_info": "large-v3",
  "timestamp": "2025-01-18T10:30:00Z",
  "version": "2.0.0"
}
```

#### 响应字段说明

| 字段 | 类型 | 描述 |
|------|------|------|
| status | string | 服务状态 (healthy/unhealthy) |
| whisper_loaded | boolean | Whisper模型是否加载 |
| device | string | 运行设备 (GPU/CPU) |
| model_info | string | 当前使用的模型 |
| timestamp | string | 响应时间戳 |
| version | string | API版本 |

## 📊 服务信息接口

### GET /

获取服务基本信息。

#### 响应格式

```json
{
  "message": "优化版语音助手API服务正在运行",
  "status": "healthy",
  "version": "2.0.0",
  "description": "支持GPU加速的中文语音识别和智能指令执行"
}
```

## 📋 支持的指令类型

### 应用程序指令

| 指令示例 | 目标应用 | 执行结果 |
|----------|----------|----------|
| "打开记事本" | notepad | 启动记事本 |
| "启动计算器" | calc | 启动计算器 |
| "运行画图" | mspaint | 启动画图程序 |
| "打开文件管理器" | explorer | 启动资源管理器 |
| "启动任务管理器" | taskmgr | 启动任务管理器 |

### 网站访问指令

| 指令示例 | 目标网站 | 执行结果 |
|----------|----------|----------|
| "打开百度" | baidu.com | 在浏览器中打开百度 |
| "访问谷歌" | google.com | 在浏览器中打开谷歌 |
| "去B站看看" | bilibili.com | 在浏览器中打开B站 |
| "打开GitHub" | github.com | 在浏览器中打开GitHub |

### 系统操作指令

| 指令示例 | 操作类型 | 执行结果 |
|----------|----------|----------|
| "锁屏" | 锁定屏幕 | 锁定当前用户会话 |
| "截图" | 截屏 | 打开截图工具 |
| "新建文件夹" | 文件操作 | 创建新文件夹 |

## 🚨 错误代码

### 通用错误

| 错误代码 | HTTP状态码 | 描述 |
|----------|------------|------|
| INTERNAL_ERROR | 500 | 服务器内部错误 |
| INVALID_REQUEST | 400 | 请求参数无效 |
| MODEL_NOT_LOADED | 500 | Whisper模型未加载 |

### 转录相关错误

| 错误代码 | HTTP状态码 | 描述 |
|----------|------------|------|
| UNSUPPORTED_FORMAT | 400 | 音频格式不支持 |
| FILE_TOO_LARGE | 413 | 文件大小超限 |
| TRANSCRIBE_FAILED | 500 | 转录处理失败 |
| NO_SPEECH_DETECTED | 400 | 未检测到语音内容 |

### 指令相关错误

| 错误代码 | HTTP状态码 | 描述 |
|----------|------------|------|
| COMMAND_FAILED | 500 | 指令执行失败 |
| UNSAFE_COMMAND | 403 | 不安全的指令 |
| PERMISSION_DENIED | 403 | 权限不足 |

## 📝 使用示例

### JavaScript前端集成

```javascript
class VoiceAPI {
    constructor(baseUrl = 'http://localhost:8889') {
        this.baseUrl = baseUrl;
    }
    
    async transcribe(audioBlob) {
        const formData = new FormData();
        formData.append('audio_file', audioBlob, 'recording.wav');
        
        const response = await fetch(`${this.baseUrl}/transcribe`, {
            method: 'POST',
            body: formData
        });
        
        return await response.json();
    }
    
    async processCommand(text, executeCommands = true) {
        const response = await fetch(`${this.baseUrl}/process`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                execute_commands: executeCommands
            })
        });
        
        return await response.json();
    }
    
    async checkHealth() {
        const response = await fetch(`${this.baseUrl}/health`);
        return await response.json();
    }
}

// 使用示例
const voiceAPI = new VoiceAPI();

// 检查服务状态
const health = await voiceAPI.checkHealth();
console.log('服务状态:', health.status);

// 处理录音
const audioBlob = new Blob([audioData], { type: 'audio/wav' });
const result = await voiceAPI.transcribe(audioBlob);

if (result.success) {
    console.log('转录结果:', result.transcribed_text);
    
    if (result.is_command) {
        console.log('检测到指令:', result.command_type);
    }
}
```

### Python客户端示例

```python
import requests
import json

class VoiceAPIClient:
    def __init__(self, base_url="http://localhost:8889"):
        self.base_url = base_url
    
    def transcribe(self, audio_file_path):
        """转录音频文件"""
        with open(audio_file_path, 'rb') as f:
            files = {'audio_file': f}
            response = requests.post(f"{self.base_url}/transcribe", files=files)
        return response.json()
    
    def process_command(self, text, execute_commands=True):
        """处理文本指令"""
        data = {
            "text": text,
            "execute_commands": execute_commands
        }
        response = requests.post(
            f"{self.base_url}/process",
            headers={'Content-Type': 'application/json'},
            data=json.dumps(data)
        )
        return response.json()
    
    def check_health(self):
        """检查服务健康状态"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()

# 使用示例
client = VoiceAPIClient()

# 检查服务状态
health = client.check_health()
print(f"服务状态: {health['status']}")

# 转录音频
result = client.transcribe("recording.wav")
if result['success']:
    print(f"转录结果: {result['transcribed_text']}")
    
    # 处理指令
    if result['is_command']:
        process_result = client.process_command(result['transcribed_text'])
        print(f"执行结果: {process_result['command_result']}")
```

## 🔧 配置选项

### 环境变量

| 变量名 | 默认值 | 描述 |
|--------|--------|------|
| VOICE_API_HOST | 0.0.0.0 | API服务监听地址 |
| VOICE_API_PORT | 8889 | API服务端口 |
| WHISPER_MODEL | large-v3 | 默认Whisper模型 |
| CUDA_VISIBLE_DEVICES | 0 | 可见的CUDA设备 |
| LOG_LEVEL | INFO | 日志级别 |

### 启动参数

```bash
python voice_api_server_optimized.py \
  --host 0.0.0.0 \
  --port 8889 \
  --model large-v3 \
  --device cuda
```

## 📈 性能指标

### 响应时间基准

| 操作 | CPU模式 | GPU模式 | 目标 |
|------|---------|---------|------|
| 转录 (10秒音频) | 3-5秒 | 1-2秒 | <3秒 |
| 指令处理 | 100ms | 100ms | <200ms |
| 健康检查 | 10ms | 10ms | <50ms |

### 并发能力

| 指标 | 数值 | 说明 |
|------|------|------|
| 最大并发转录 | 5 | 受GPU内存限制 |
| 最大并发指令 | 50 | CPU密集型操作 |
| 连接超时 | 30秒 | 长音频处理时间 |

## 🔍 调试和监控

### 日志格式

```
2025-01-18 10:30:00,123 - voice_api - INFO - 转录请求: audio_length=10.5s
2025-01-18 10:30:02,456 - voice_api - INFO - 转录完成: text="打开记事本", confidence=0.95
2025-01-18 10:30:02,500 - voice_api - INFO - 指令执行: type=应用程序, target=记事本, result=success
```

### 监控端点

```bash
# 服务状态
curl http://localhost:8889/health

# 详细信息
curl http://localhost:8889/

# 错误日志
tail -f voice_assistant.log | grep ERROR
```

---

*API文档版本: v2.0.0 | 最后更新: 2025-01-18*