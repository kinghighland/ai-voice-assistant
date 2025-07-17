/**
 * Open WebUI 语音助手插件
 * 提供语音输入和智能命令执行功能
 */

class VoiceAssistantPlugin {
    constructor() {
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.apiBaseUrl = 'http://localhost:8001'; // 语音API服务地址
        this.init();
    }

    init() {
        this.createUI();
        this.bindEvents();
        console.log('语音助手插件已初始化');
    }

    createUI() {
        // 创建语音按钮
        const voiceButton = document.createElement('button');
        voiceButton.id = 'voice-assistant-btn';
        voiceButton.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
            </svg>
        `;
        voiceButton.className = 'voice-btn';
        voiceButton.title = '按住录音，松开发送';

        // 添加样式
        const style = document.createElement('style');
        style.textContent = `
            .voice-btn {
                background: #4CAF50;
                border: none;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                color: white;
                cursor: pointer;
                position: fixed;
                bottom: 20px;
                right: 20px;
                z-index: 1000;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                transition: all 0.3s ease;
            }
            
            .voice-btn:hover {
                background: #45a049;
                transform: scale(1.1);
            }
            
            .voice-btn.recording {
                background: #f44336;
                animation: pulse 1s infinite;
            }
            
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.1); }
                100% { transform: scale(1); }
            }
            
            .voice-status {
                position: fixed;
                bottom: 80px;
                right: 20px;
                background: rgba(0,0,0,0.8);
                color: white;
                padding: 10px 15px;
                border-radius: 20px;
                font-size: 14px;
                z-index: 1001;
                display: none;
            }
            
            .voice-transcript {
                position: fixed;
                bottom: 120px;
                right: 20px;
                background: rgba(255,255,255,0.95);
                color: #333;
                padding: 15px;
                border-radius: 10px;
                max-width: 300px;
                font-size: 14px;
                z-index: 1001;
                display: none;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
        `;
        document.head.appendChild(style);

        // 创建状态显示
        const statusDiv = document.createElement('div');
        statusDiv.id = 'voice-status';
        statusDiv.className = 'voice-status';

        const transcriptDiv = document.createElement('div');
        transcriptDiv.id = 'voice-transcript';
        transcriptDiv.className = 'voice-transcript';

        // 添加到页面
        document.body.appendChild(voiceButton);
        document.body.appendChild(statusDiv);
        document.body.appendChild(transcriptDiv);
    }

    bindEvents() {
        const voiceBtn = document.getElementById('voice-assistant-btn');

        // 鼠标事件
        voiceBtn.addEventListener('mousedown', (e) => {
            e.preventDefault();
            this.startRecording();
        });

        voiceBtn.addEventListener('mouseup', (e) => {
            e.preventDefault();
            this.stopRecording();
        });

        voiceBtn.addEventListener('mouseleave', (e) => {
            if (this.isRecording) {
                this.stopRecording();
            }
        });

        // 触摸事件（移动端支持）
        voiceBtn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.startRecording();
        });

        voiceBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.stopRecording();
        });
    }

    async startRecording() {
        if (this.isRecording) return;

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };

            this.mediaRecorder.onstop = () => {
                this.processAudio();
            };

            this.mediaRecorder.start();
            this.isRecording = true;

            // 更新UI
            const voiceBtn = document.getElementById('voice-assistant-btn');
            const statusDiv = document.getElementById('voice-status');

            voiceBtn.classList.add('recording');
            statusDiv.textContent = '🎤 录音中...';
            statusDiv.style.display = 'block';

            console.log('开始录音');

        } catch (error) {
            console.error('录音失败:', error);
            this.showStatus('❌ 无法访问麦克风');
        }
    }

    stopRecording() {
        if (!this.isRecording) return;

        this.mediaRecorder.stop();
        this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        this.isRecording = false;

        // 更新UI
        const voiceBtn = document.getElementById('voice-assistant-btn');
        voiceBtn.classList.remove('recording');

        this.showStatus('🔄 处理中...');
        console.log('停止录音');
    }

    async processAudio() {
        try {
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });

            // 发送音频到后端进行转录
            const formData = new FormData();
            formData.append('audio_file', audioBlob, 'recording.wav');

            const transcribeResponse = await fetch(`${this.apiBaseUrl}/transcribe`, {
                method: 'POST',
                body: formData
            });

            if (!transcribeResponse.ok) {
                throw new Error('转录失败');
            }

            const transcribeResult = await transcribeResponse.json();
            const transcribedText = transcribeResult.transcribed_text;

            if (!transcribedText) {
                this.showStatus('❌ 未检测到语音');
                return;
            }

            console.log('转录结果:', transcribedText);
            this.showTranscript(`您说的是: ${transcribedText}`);

            // 处理命令
            const processResponse = await fetch(`${this.apiBaseUrl}/process`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: transcribedText,
                    execute_commands: true
                })
            });

            if (!processResponse.ok) {
                throw new Error('处理失败');
            }

            const processResult = await processResponse.json();

            // 显示结果
            let resultText = processResult.ai_response;
            if (processResult.command_executed && processResult.command_result) {
                resultText = processResult.command_result;
            }

            // 将结果插入到Open WebUI的聊天界面
            this.insertMessageToChat(transcribedText, resultText);

            this.showStatus('✅ 完成');
            setTimeout(() => this.hideStatus(), 2000);

        } catch (error) {
            console.error('处理音频失败:', error);
            this.showStatus('❌ 处理失败');
            setTimeout(() => this.hideStatus(), 3000);
        }
    }

    insertMessageToChat(userMessage, aiResponse) {
        // 尝试找到Open WebUI的输入框并插入消息
        const chatInput = document.querySelector('textarea[placeholder*="Send a message"]') ||
            document.querySelector('textarea') ||
            document.querySelector('input[type="text"]');

        if (chatInput) {
            // 插入用户消息
            chatInput.value = `🎤 ${userMessage}`;

            // 触发输入事件
            const inputEvent = new Event('input', { bubbles: true });
            chatInput.dispatchEvent(inputEvent);

            // 尝试找到发送按钮并点击
            setTimeout(() => {
                const sendButton = document.querySelector('button[type="submit"]') ||
                    document.querySelector('button:contains("Send")') ||
                    document.querySelector('[data-testid="send-button"]');

                if (sendButton) {
                    sendButton.click();
                }
            }, 100);
        } else {
            // 如果找不到输入框，显示在转录区域
            this.showTranscript(`用户: ${userMessage}\n\nAI: ${aiResponse}`);
        }
    }

    showStatus(message) {
        const statusDiv = document.getElementById('voice-status');
        statusDiv.textContent = message;
        statusDiv.style.display = 'block';
    }

    hideStatus() {
        const statusDiv = document.getElementById('voice-status');
        const transcriptDiv = document.getElementById('voice-transcript');
        statusDiv.style.display = 'none';
        transcriptDiv.style.display = 'none';
    }

    showTranscript(text) {
        const transcriptDiv = document.getElementById('voice-transcript');
        transcriptDiv.textContent = text;
        transcriptDiv.style.display = 'block';

        // 5秒后自动隐藏
        setTimeout(() => {
            transcriptDiv.style.display = 'none';
        }, 5000);
    }
}

// 当页面加载完成后初始化插件
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new VoiceAssistantPlugin();
    });
} else {
    new VoiceAssistantPlugin();
}