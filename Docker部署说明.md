# 🐳 Docker部署说明

## 🎯 部署方式对比

### 方式1: 混合部署 (推荐)
- **Open WebUI**: Docker容器
- **语音助手**: 主机运行
- **优势**: GPU直接访问，性能最佳
- **适用**: 开发和个人使用

### 方式2: 完全容器化
- **Open WebUI**: Docker容器  
- **语音助手**: Docker容器
- **优势**: 环境隔离，易于部署
- **适用**: 生产环境和团队使用

## 🚀 快速开始

### 方式1: 混合部署

#### 1. 启动Open WebUI
```bash
docker-compose up -d
```

#### 2. 启动语音助手 (主机)
```bash
# 安装依赖
pip install -r requirements.txt

# 下载模型
python download_whisper_modelscope.py

# 启动服务
python start.py
```

### 方式2: 完全容器化

#### 前置要求
```bash
# 安装nvidia-docker (GPU支持)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

#### 启动服务
```bash
# 构建并启动所有服务
docker-compose -f docker-compose-full.yml up -d

# 查看日志
docker-compose -f docker-compose-full.yml logs -f voice-assistant
```

## 📊 配置说明

### GPU支持配置

#### Docker Compose配置
```yaml
voice-assistant:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
  environment:
    - CUDA_VISIBLE_DEVICES=0
    - PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
```

#### 环境变量
- `CUDA_VISIBLE_DEVICES=0` - 指定GPU设备
- `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` - 优化内存分配

### 数据卷配置

#### Whisper模型缓存
```yaml
volumes:
  - whisper-cache:/root/.cache/whisper
```

#### 静态文件挂载
```yaml
volumes:
  - ./static:/app/static
```

## 🔧 常用命令

### 服务管理
```bash
# 启动服务
docker-compose -f docker-compose-full.yml up -d

# 停止服务
docker-compose -f docker-compose-full.yml down

# 重启语音助手
docker-compose -f docker-compose-full.yml restart voice-assistant

# 查看服务状态
docker-compose -f docker-compose-full.yml ps
```

### 日志查看
```bash
# 查看所有服务日志
docker-compose -f docker-compose-full.yml logs

# 查看语音助手日志
docker-compose -f docker-compose-full.yml logs voice-assistant

# 实时日志
docker-compose -f docker-compose-full.yml logs -f voice-assistant
```

### 容器管理
```bash
# 进入语音助手容器
docker exec -it voice-assistant bash

# 检查GPU状态
docker exec voice-assistant python test_gpu.py

# 手动下载模型
docker exec voice-assistant python download_whisper_modelscope.py
```

## 🛠️ 故障排除

### 常见问题

#### 1. GPU不可用
**症状**: 容器内检测不到GPU
**解决方案**:
```bash
# 检查nvidia-docker安装
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# 检查Docker配置
docker info | grep nvidia
```

#### 2. 模型下载失败
**症状**: Whisper模型下载超时
**解决方案**:
```bash
# 预先下载模型到主机
python download_whisper_modelscope.py

# 挂载模型缓存
docker run -v ~/.cache/whisper:/root/.cache/whisper voice-assistant
```

#### 3. 内存不足
**症状**: CUDA out of memory
**解决方案**:
```bash
# 设置内存限制
docker run --gpus all --memory=8g voice-assistant

# 使用更小的模型
# 修改voice_api_server.py中的model_priority
```

#### 4. 网络连接问题
**症状**: Open WebUI无法连接语音API
**解决方案**:
```bash
# 检查网络连接
docker network ls
docker network inspect ai-voice-assistant_default

# 测试API连接
curl http://localhost:8889/health
```

## 📈 性能优化

### 容器资源限制
```yaml
voice-assistant:
  deploy:
    resources:
      limits:
        memory: 8G
        cpus: '4'
      reservations:
        memory: 4G
        cpus: '2'
```

### GPU内存优化
```yaml
environment:
  - PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
  - CUDA_LAUNCH_BLOCKING=1
```

### 网络优化
```yaml
networks:
  voice-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

## 🔒 安全配置

### 生产环境建议
```yaml
# 限制端口暴露
ports:
  - "127.0.0.1:8889:8889"  # 只允许本地访问

# 设置安全密钥
environment:
  - WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY}
  - API_SECRET_KEY=${API_SECRET_KEY}

# 只读挂载
volumes:
  - ./static:/app/static:ro
```

### 网络安全
```yaml
# 创建专用网络
networks:
  voice-network:
    driver: bridge
    internal: true  # 内部网络
```

## 📋 部署检查清单

### 部署前检查
- [ ] Docker和docker-compose已安装
- [ ] nvidia-docker已安装 (GPU用户)
- [ ] 端口8888和8889未被占用
- [ ] 有足够的磁盘空间 (>5GB)

### 部署后验证
- [ ] Open WebUI可访问 (http://localhost:8888)
- [ ] 语音API健康检查通过 (http://localhost:8889/health)
- [ ] GPU状态正常 (如果使用GPU)
- [ ] 语音功能正常工作

### 性能验证
- [ ] 语音转录响应时间 < 3秒
- [ ] 指令执行成功率 > 90%
- [ ] GPU内存使用合理
- [ ] 容器资源使用正常

## 🎯 推荐配置

### 开发环境
```bash
# 使用混合部署
docker-compose up -d  # 只启动Open WebUI
python start.py  # 主机运行语音助手
```

### 生产环境
```bash
# 使用完全容器化
docker-compose -f docker-compose-full.yml up -d
```

### 测试环境
```bash
# 使用CPU模式
docker-compose -f docker-compose-full.yml up -d
# 修改环境变量: CUDA_VISIBLE_DEVICES=""
```

---

**Docker支持状态**: ✅ 完全兼容  
**推荐部署方式**: 混合部署 (开发) / 完全容器化 (生产)  
**GPU支持**: ✅ nvidia-docker  
**最后更新**: 2025-01-18