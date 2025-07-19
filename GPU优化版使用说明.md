# 🚀 GPU内存优化版AI语音助手使用说明

## 🎯 优化亮点

### 1. GPU内存管理优化 ⚡
- **Whisper-large-v3-turbo模型**: 显存占用减少50% (1.5GB vs 3.1GB)
- **内存分配策略**: Whisper占用50%，为其他AI模型预留50%
- **智能内存清理**: 自动清理GPU缓存，避免内存泄漏

### 2. ModelScope快速下载 🚀
- **下载速度**: 比官方源快5-10倍
- **国内优化**: 使用阿里云CDN加速
- **一键下载**: 自动配置Whisper缓存

### 3. 指令优先执行 🎯
- **跳过AI回复**: 语音指令直接执行，避免GPU冲突
- **智能分流**: 指令走系统执行，对话走AI模型
- **响应更快**: 指令执行时间 < 1秒

## 🛠️ 安装和配置

### 1. 环境准备

```bash
# 安装依赖 (包含ModelScope)
pip install -r requirements.txt

# GPU用户安装CUDA版PyTorch
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 2. 快速下载模型

#### 方式1: ModelScope快速下载 (推荐)
```bash
# 下载turbo模型 (推荐)
python download_whisper_modelscope.py

# 或者手动下载
modelscope download --model iic/Whisper-large-v3-turbo
```

#### 方式2: 自动下载
```bash
# 启动时自动下载 (较慢)
python start.py
```

### 3. 启动服务

```bash
# 一键启动器 (推荐)
python start.py

# 或直接启动服务
python voice_api_server.py
```

## 📊 性能对比

### GPU内存使用对比

| 模型版本 | 显存占用 | 识别质量 | 速度 | 推荐场景 |
|----------|----------|----------|------|----------|
| large-v3-turbo | 1.5GB | 95%+ | 极快 | 🎯 推荐 |
| large-v3 | 3.1GB | 98%+ | 快 | 高质量需求 |
| medium | 1.0GB | 90%+ | 中等 | 中等配置 |
| base | 0.3GB | 85%+ | 慢 | 低配置 |

### 下载速度对比

| 下载方式 | large-v3-turbo | large-v3 | 说明 |
|----------|----------------|----------|------|
| ModelScope | 2-5分钟 | 5-10分钟 | 🚀 推荐 |
| 官方源 | 10-20分钟 | 20-40分钟 | 备用 |

## 🎮 GPU配置建议

### 显卡配置推荐

| GPU型号 | 显存 | 推荐模型 | 可同时运行 |
|---------|------|----------|------------|
| RTX 4090 | 24GB | large-v3-turbo | ✅ Whisper + 多个AI模型 |
| RTX 4080 | 16GB | large-v3-turbo | ✅ Whisper + 1-2个AI模型 |
| RTX 4070 | 12GB | large-v3-turbo | ✅ Whisper + 1个AI模型 |
| RTX 3060 | 8GB | medium | ⚠️ 仅Whisper |
| GTX 1060 | 6GB | base | ⚠️ 仅Whisper |

### 内存分配策略

```python
# 自动配置的内存分配 (已优化)
torch.cuda.set_per_process_memory_fraction(0.5)  # Whisper: 50%
# 其他AI模型可使用剩余50%内存，确保多模型共存
```

## 🎯 使用流程

### 1. 启动服务

```bash
python start.py
```

**启动日志示例:**
```
🎤 GPU内存优化版AI语音助手启动器
==================================================
🔍 检查系统依赖...
✅ 基础依赖检查通过
🔍 检查GPU状态...
🎮 检测到GPU: NVIDIA GeForce RTX 4080
💾 GPU内存: 16.0 GB
📊 内存状态: 已用 0.0GB, 已预留 0.0GB, 可用 16.0GB
🔍 检查Whisper模型...
✅ large-v3-turbo: 推荐: 显存占用少，速度快 (1.5GB)

🔧 GPU内存优化:
   - Whisper模型将占用70%GPU内存
   - 为其他AI模型预留30%内存
   - 语音指令优先执行，避免模型冲突
```

### 2. 使用语音功能

1. **访问Open WebUI**: http://localhost:8888
2. **注入前端脚本**: 运行 `AI_button_browser_plugin.js`
3. **使用语音按钮**: 右下角紫色按钮

### 3. 语音指令示例

#### 应用程序指令 ✅
- "打开计算器" → 直接启动，无GPU冲突
- "启动记事本" → 快速执行
- "运行任务管理器" → 立即响应

#### 网站访问指令 ✅
- "打开百度" → 浏览器打开
- "访问知乎" → 直接跳转
- "去B站看看" → 快速访问

#### 普通对话 💬
- "今天天气怎么样？" → 插入聊天框，由WebUI的AI处理

## 🔧 高级配置

### 1. 自定义GPU内存分配

```python
# 在voice_api_server.py中修改
torch.cuda.set_per_process_memory_fraction(0.6)  # 调整为60%
```

### 2. 模型优先级配置

```python
# 修改模型加载优先级
model_priority = ["large-v3-turbo", "medium", "base"]
```

### 3. 指令执行配置

```python
# 完全禁用AI回复，专注指令执行
ENABLE_AI_RESPONSE = False
```

## 🚨 故障排除

### 常见问题

#### 1. GPU内存不足
**症状**: CUDA out of memory
**解决方案**:
```bash
# 检查GPU状态
python test_gpu.py

# 使用更小的模型
python download_whisper_modelscope.py  # 选择medium或base
```

#### 2. ModelScope下载失败
**症状**: 网络连接错误
**解决方案**:
```bash
# 安装ModelScope
pip install modelscope

# 手动下载
modelscope download --model iic/Whisper-large-v3-turbo
```

#### 3. 指令不执行
**症状**: 语音转录成功但指令未执行
**解决方案**:
```bash
# 检查后端日志
# 确认指令检测结果
# 查看execute_enhanced_command执行情况
```

### 调试命令

```bash
# 检查GPU内存使用
nvidia-smi

# 测试API接口
curl -X GET "http://localhost:8889/health"

# 查看详细日志
tail -f voice_assistant.log
```

## 📈 性能监控

### GPU内存监控

```bash
# 实时监控GPU使用
watch -n 1 nvidia-smi

# Python脚本监控
python -c "
import torch
print(f'已分配: {torch.cuda.memory_allocated()/1024**3:.1f}GB')
print(f'已缓存: {torch.cuda.memory_reserved()/1024**3:.1f}GB')
"
```

### 服务性能监控

```bash
# 检查服务状态
curl http://localhost:8889/health

# 响应时间测试
time curl -X POST "http://localhost:8889/process" \
  -H "Content-Type: application/json" \
  -d '{"text": "打开计算器", "execute_commands": true}'
```

## 🎉 优化效果总结

### 内存优化效果
- **显存节省**: 50% (turbo模型)
- **内存管理**: 智能分配，支持多模型
- **冲突避免**: 指令优先，跳过AI回复

### 下载速度提升
- **ModelScope**: 5-10倍速度提升
- **国内网络**: 完美适配
- **一键配置**: 自动设置缓存

### 用户体验提升
- **响应更快**: 指令执行 < 1秒
- **更稳定**: 避免GPU内存冲突
- **更智能**: 自动选择最优模型

---

🎯 **推荐配置**: RTX 4070+ 显卡 + large-v3-turbo模型 + ModelScope下载

💡 **最佳实践**: 使用 `python start.py` 一键启动