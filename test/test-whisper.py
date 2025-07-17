import whisper
model = whisper.load_model("base")
result = model.transcribe("test.mp3")  # 替换为您的音频文件
print(result["text"])