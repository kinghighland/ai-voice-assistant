// Open WebUI 语音助手集成脚本
// 将此代码复制到 Open WebUI 的自定义 JavaScript 设置中

(function () {
    'use strict';

    // 语音助手API配置
    const VOICE_API_URL = 'http://localhost:8889';

    // 创建语音按钮
    function createVoiceButton() {
        const voiceButton = document.createElement('button');
        voiceButton.id = 'voice-assistant-btn';
        voiceButton.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
            </svg>
        `;

        // 样式
        Object.assign(voiceButton.style, {
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            width: '50px',
            height: '50px',
            borderRadius: '50%',
            border: 'none',
            background: '#4CAF50',
            color: 'white',
            cursor: 'pointer',
            zIndex: '1000',
            boxShadow: '0 4px 8px rgba(0,0,0,0.2)',
            transition: 'all 0.3s ease'
        });

        voiceButton.title = '按住录音，松开发送';
        return voiceButton;
    }

    // 语音录制类
    class VoiceRecorder {
        constructor() {
            this.isRecording = false;
            this.mediaRecorder = null;
            this.audioChunks = [];
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

                // 更新按钮样式
                const btn = document.getElementById('voice-assistant-btn');
                btn.style.background = '#f44336';
                btn.style.animation = 'pulse 1s infinite';

                console.log('开始录音');

            } catch (error) {
                console.error('录音失败:', error);
                alert('无法访问麦克风，请检查权限设置');
            }
        }

        stopRecording() {
            if (!this.isRecording) return;

            this.mediaRecorder.stop();
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            this.isRecording = false;

            // 恢复按钮样式
            const btn = document.getElementById('voice-assistant-btn');
            btn.style.background = '#4CAF50';
            btn.style.animation = 'none';

            console.log('停止录音');
        }

        async processAudio() {
            try {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });

                // 发送到语音API进行转录
                const formData = new FormData();
                formData.append('audio_file', audioBlob, 'recording.wav');

                const response = await fetch(`${VOICE_API_URL}/transcribe`, {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error('转录失败');
                }

                const result = await response.json();
                const transcribedText = result.transcribed_text;

                if (transcribedText) {
                    // 将转录文本插入到聊天输入框
                    this.insertTextToChat(transcribedText);
                } else {
                    alert('未检测到语音内容');
                }

            } catch (error) {
                console.error('处理音频失败:', error);
                alert('语音处理失败，请重试');
            }
        }

        insertTextToChat(text) {
            // 查找Open WebUI的输入框
            const chatInput = document.querySelector('textarea[placeholder*="Send a message"]') ||
                document.querySelector('textarea') ||
                document.querySelector('input[type="text"]');

            if (chatInput) {
                chatInput.value = `🎤 ${text}`;

                // 触发输入事件
                const inputEvent = new Event('input', { bubbles: true });
                chatInput.dispatchEvent(inputEvent);

                // 聚焦到输入框
                chatInput.focus();

                console.log('已插入语音转录文本:', text);
            } else {
                console.error('未找到聊天输入框');
                // 作为备选方案，复制到剪贴板
                navigator.clipboard.writeText(text).then(() => {
                    alert(`语音转录完成，文本已复制到剪贴板：\n${text}`);
                });
            }
        }
    }

    // 初始化语音助手
    function initVoiceAssistant() {
        // 添加CSS动画
        const style = document.createElement('style');
        style.textContent = `
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.1); }
                100% { transform: scale(1); }
            }
        `;
        document.head.appendChild(style);

        // 创建语音按钮
        const voiceButton = createVoiceButton();
        document.body.appendChild(voiceButton);

        // 创建录音器
        const recorder = new VoiceRecorder();

        // 绑定事件
        voiceButton.addEventListener('mousedown', (e) => {
            e.preventDefault();
            recorder.startRecording();
        });

        voiceButton.addEventListener('mouseup', (e) => {
            e.preventDefault();
            recorder.stopRecording();
        });

        voiceButton.addEventListener('mouseleave', (e) => {
            if (recorder.isRecording) {
                recorder.stopRecording();
            }
        });

        // 触摸事件支持
        voiceButton.addEventListener('touchstart', (e) => {
            e.preventDefault();
            recorder.startRecording();
        });

        voiceButton.addEventListener('touchend', (e) => {
            e.preventDefault();
            recorder.stopRecording();
        });

        console.log('语音助手已初始化');
    }

    // 等待页面加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initVoiceAssistant);
    } else {
        initVoiceAssistant();
    }

})();