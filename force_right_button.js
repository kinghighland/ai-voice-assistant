// 强制在右下角创建AI语音按钮
// 完全独立，不依赖任何现有按钮

(function () {
    'use strict';

    console.log('🎯 强制创建右下角AI语音按钮...');

    // 彻底清理所有可能的旧元素
    const cleanupSelectors = [
        '#ai-voice-button',
        '#enhanced-voice-btn',
        '#voice-status-indicator',
        '#ai-voice-status',
        '#ai-voice-styles',
        '#voice-enhancer-styles',
        '.ai-voice-button',
        '.enhanced-voice-btn'
    ];

    cleanupSelectors.forEach(selector => {
        document.querySelectorAll(selector).forEach(el => {
            el.remove();
            console.log(`🗑️ 清理: ${selector}`);
        });
    });

    // 移除所有增强标识
    document.querySelectorAll('button').forEach(btn => {
        if (btn.getAttribute('data-enhanced')) {
            btn.removeAttribute('data-enhanced');
            btn.title = btn.title.replace(' (增强版)', '');
            console.log('🧹 移除增强标识');
        }
    });

    // 配置
    const API_URL = 'http://localhost:8889';

    // 全局变量
    let isRecording = false;
    let mediaRecorder = null;
    let audioChunks = [];

    // 创建样式
    function createStyles() {
        const style = document.createElement('style');
        style.id = 'force-voice-styles';
        style.textContent = `
            #force-voice-btn {
                position: fixed !important;
                bottom: 120px !important;
                right: 30px !important;
                width: 70px !important;
                height: 70px !important;
                border-radius: 50% !important;
                background: linear-gradient(135deg, #8B5CF6, #7C3AED) !important;
                border: 3px solid white !important;
                color: white !important;
                cursor: pointer !important;
                z-index: 99999 !important;
                box-shadow: 0 4px 20px rgba(139, 92, 246, 0.5) !important;
                transition: all 0.3s ease !important;
                display: flex !important;
                flex-direction: column !important;
                align-items: center !important;
                justify-content: center !important;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
                font-size: 10px !important;
                font-weight: bold !important;
                text-align: center !important;
            }
            
            #force-voice-btn:hover {
                transform: scale(1.1) !important;
                box-shadow: 0 6px 25px rgba(139, 92, 246, 0.7) !important;
            }
            
            #force-voice-btn.recording {
                background: linear-gradient(135deg, #EF4444, #DC2626) !important;
                animation: voice-pulse 1s infinite !important;
            }
            
            #force-voice-status {
                position: fixed !important;
                top: 20px !important;
                right: 20px !important;
                padding: 12px 16px !important;
                border-radius: 25px !important;
                color: white !important;
                font-size: 14px !important;
                font-weight: 500 !important;
                z-index: 99998 !important;
                display: none !important;
                max-width: 300px !important;
                backdrop-filter: blur(10px) !important;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
            }
            
            #force-voice-status.success {
                background: rgba(34, 197, 94, 0.9) !important;
            }
            
            #force-voice-status.error {
                background: rgba(239, 68, 68, 0.9) !important;
            }
            
            #force-voice-status.recording {
                background: rgba(239, 68, 68, 0.9) !important;
                animation: voice-pulse 1s infinite !important;
            }
            
            #force-voice-status.processing {
                background: rgba(168, 85, 247, 0.9) !important;
            }
            
            @keyframes voice-pulse {
                0% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.8; transform: scale(1.05); }
                100% { opacity: 1; transform: scale(1); }
            }
        `;
        document.head.appendChild(style);
        console.log('✅ 样式已创建');
    }

    // 创建按钮
    function createButton() {
        const button = document.createElement('button');
        button.id = 'force-voice-btn';
        button.innerHTML = `
            🎤<br>
            AI语音
        `;
        button.title = '按住录音，松开发送';

        // 确保添加到body的最后
        document.body.appendChild(button);

        // 绑定事件
        button.addEventListener('mousedown', startRecording);
        button.addEventListener('mouseup', stopRecording);
        button.addEventListener('mouseleave', () => {
            if (isRecording) stopRecording();
        });

        // 触摸事件
        button.addEventListener('touchstart', (e) => {
            e.preventDefault();
            startRecording();
        });
        button.addEventListener('touchend', (e) => {
            e.preventDefault();
            stopRecording();
        });

        console.log('✅ 按钮已创建在右下角');
        return button;
    }

    // 创建状态指示器
    function createStatus() {
        const status = document.createElement('div');
        status.id = 'force-voice-status';
        document.body.appendChild(status);
        console.log('✅ 状态指示器已创建');
    }

    // 显示状态
    function showStatus(message, type = 'info', duration = 3000) {
        const status = document.getElementById('force-voice-status');
        if (!status) return;

        status.textContent = message;
        status.className = '';
        status.classList.add(type);
        status.style.display = 'block';

        setTimeout(() => {
            status.style.display = 'none';
        }, duration);
    }

    // 开始录音
    async function startRecording() {
        if (isRecording) return;

        console.log('🎤 开始录音...');
        showStatus('🎤 录音中...', 'recording');

        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });

            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            isRecording = true;

            const button = document.getElementById('force-voice-btn');
            button.classList.add('recording');

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = () => {
                stream.getTracks().forEach(track => track.stop());
                processAudio();
            };

            mediaRecorder.start();

        } catch (error) {
            console.error('录音失败:', error);
            showStatus('❌ 无法访问麦克风', 'error');
            isRecording = false;
        }
    }

    // 停止录音
    function stopRecording() {
        if (!isRecording) return;

        console.log('⏹️ 停止录音...');
        showStatus('🔄 处理中...', 'processing');

        mediaRecorder.stop();
        isRecording = false;

        const button = document.getElementById('force-voice-btn');
        button.classList.remove('recording');
    }

    // 处理音频
    async function processAudio() {
        try {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });

            const formData = new FormData();
            formData.append('audio_file', audioBlob, 'recording.wav');

            const response = await fetch(`${API_URL}/transcribe`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`转录失败: ${response.status}`);
            }

            const result = await response.json();
            const text = result.transcribed_text;

            if (!text || text.trim() === '') {
                showStatus('❌ 未检测到语音', 'error');
                return;
            }

            console.log('✅ 转录结果:', text);
            showStatus(`✅ "${text}"`, 'success');

            insertText(text);

        } catch (error) {
            console.error('处理失败:', error);
            showStatus(`❌ ${error.message}`, 'error');
        }
    }

    // 检查是否为语音指令
    function isVoiceCommand(text) {
        const commands = [
            '打开', '启动', '运行', '执行', '关闭', '停止',
            'open', 'start', 'run', 'execute', 'close', 'stop',
            '计算器', 'calculator', '记事本', 'notepad',
            '浏览器', 'browser', '文件管理器', 'explorer'
        ];

        return commands.some(cmd => text.toLowerCase().includes(cmd.toLowerCase()));
    }

    // 处理语音指令
    async function handleVoiceCommand(text) {
        try {
            const response = await fetch(`${API_URL}/process`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text,
                    execute_commands: true
                })
            });

            if (!response.ok) {
                throw new Error(`指令处理失败: ${response.status}`);
            }

            const result = await response.json();

            if (result.command_executed) {
                showStatus(`✅ 已执行: ${text}`, 'success', 5000);
                console.log('指令执行结果:', result.command_result);

                // 显示执行结果
                if (result.command_result) {
                    setTimeout(() => {
                        showStatus(`结果: ${result.command_result}`, 'info', 8000);
                    }, 2000);
                }
            } else {
                // 如果不是指令，当作普通文本处理
                insertTextToChat(text);
            }

        } catch (error) {
            console.error('指令处理失败:', error);
            showStatus('⚠️ 指令处理失败，作为文本插入', 'error');
            insertTextToChat(text);
        }
    }

    // 插入文本到聊天框
    function insertTextToChat(text) {
        const selectors = [
            'textarea[placeholder*="Send a message"]',
            'textarea[placeholder*="message"]',
            'textarea[placeholder*="Send"]',
            'div[contenteditable="true"]',
            'textarea[rows]',
            'textarea',
            'input[type="text"]'
        ];

        let input = null;

        // 更全面的查找方式
        for (const selector of selectors) {
            const elements = document.querySelectorAll(selector);
            for (const el of elements) {
                // 检查元素是否可见且可编辑
                const rect = el.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0 && !el.disabled && !el.readOnly) {
                    input = el;
                    break;
                }
            }
            if (input) break;
        }

        // 如果还是找不到，尝试最后一个textarea
        if (!input) {
            const textareas = Array.from(document.querySelectorAll('textarea'));
            input = textareas[textareas.length - 1];
        }

        if (input) {
            console.log('🎯 找到输入框:', input);

            // 清空并设置焦点
            input.focus();
            input.value = '';

            // 设置文本
            input.value = text;

            // 如果是contenteditable元素
            if (input.contentEditable === 'true') {
                input.textContent = text;
                input.innerHTML = text;
            }

            // 触发多种事件确保框架检测到变化
            const events = [
                new Event('focus', { bubbles: true }),
                new Event('input', { bubbles: true }),
                new Event('change', { bubbles: true }),
                new Event('keyup', { bubbles: true }),
                new Event('keydown', { bubbles: true }),
                new InputEvent('input', { bubbles: true, inputType: 'insertText', data: text })
            ];

            events.forEach(event => {
                try {
                    input.dispatchEvent(event);
                } catch (e) {
                    console.warn('事件触发失败:', e);
                }
            });

            // React/Vue兼容性处理
            setTimeout(() => {
                try {
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                        window.HTMLTextAreaElement.prototype, "value"
                    )?.set;

                    if (nativeInputValueSetter) {
                        nativeInputValueSetter.call(input, text);
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                } catch (e) {
                    console.warn('React/Vue兼容性处理失败:', e);
                }
            }, 100);

            showStatus('✅ 文本已插入', 'success');

            // 询问是否发送
            setTimeout(() => {
                if (confirm('🚀 发送消息？')) {
                    sendMessage();
                }
            }, 800);

        } else {
            console.warn('⚠️ 未找到输入框');
            showStatus(`转录结果: "${text}"`, 'info', 10000);

            // 调试信息
            console.log('页面中的所有可能输入元素:');
            document.querySelectorAll('textarea, input, [contenteditable]').forEach((el, i) => {
                console.log(`${i}: ${el.tagName} - ${el.placeholder || el.getAttribute('aria-label') || 'no label'}`);
            });
        }
    }

    // 发送消息
    function sendMessage() {
        const sendSelectors = [
            'button[type="submit"]',
            'button[aria-label*="Send"]',
            'button[aria-label*="发送"]',
            'button[title*="Send"]',
            'button[title*="发送"]',
            '[data-testid="send-button"]',
            '.send-button'
        ];

        for (const selector of sendSelectors) {
            const button = document.querySelector(selector);
            if (button && button.offsetParent !== null && !button.disabled) {
                button.click();
                showStatus('📤 消息已发送', 'success');
                return;
            }
        }

        showStatus('⚠️ 请手动点击发送', 'error');
    }

    // 主要的文本处理函数
    function insertText(text) {
        // 首先检查是否为语音指令
        if (isVoiceCommand(text)) {
            console.log('🎯 检测到语音指令:', text);
            showStatus('🔧 执行指令中...', 'processing');
            handleVoiceCommand(text);
        } else {
            console.log('💬 普通文本消息:', text);
            insertTextToChat(text);
        }
    }

    // 测试API连接
    async function testAPI() {
        try {
            const response = await fetch(`${API_URL}/health`);
            if (response.ok) {
                showStatus('✅ API已连接', 'success');
            } else {
                showStatus('⚠️ API异常', 'error');
            }
        } catch (error) {
            showStatus('❌ API未连接', 'error');
        }
    }

    // 初始化
    function init() {
        createStyles();
        createButton();
        createStatus();
        testAPI();

        console.log('🎉 强制右下角AI语音按钮已就绪！');
        console.log('📍 位置: 右下角，距离底部120px，距离右边30px');
        console.log('🎤 使用: 按住按钮录音，松开发送');
    }

    // 延迟初始化，确保页面完全加载
    setTimeout(init, 1000);

})();