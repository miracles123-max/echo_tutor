import os
import sys
import httpx
import json
from pydantic_settings import BaseSettings, SettingsConfigDict

class DiagnosticSettings(BaseSettings):
    modelscope_api_key: str = ""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

def diagnose():
    print("--- 诊断开始 ---")
    cwd = os.getcwd()
    print(f"当前工作目录: {cwd}")
    
    env_exists = os.path.exists(".env")
    print(f".env 文件是否存在: {'是' if env_exists else '否'}")
    
    if env_exists:
        with open(".env", "r") as f:
            content = f.read()
            print(f".env 文件行数: {len(content.splitlines())}")
            if "MODELSCOPE_API_KEY" not in content:
                print("警告: .env 中未找到 MODELSCOPE_API_KEY 关键字")
    
    settings = DiagnosticSettings()
    key = settings.modelscope_api_key
    
    if not key:
        print("错误: 无法从 .env 加载 API Key")
    else:
        # Mask the key for safety
        masked = key[:4] + "***" + key[-4:] if len(key) > 8 else "***"
        print(f"当前加载的 Key (已脱敏): {masked}")
        print(f"Key 长度: {len(key)}")
        
        if key.startswith("ms-"):
            print("🔴 发现问题: 你的 Key 以 'ms-' 开头，这是旧版 ModelScope Key。")
            print("👉 请替换为以 'sk-' 开头的真实 DashScope API Key。")
        elif key.startswith("sk-"):
            print("🟢 Key 格式看起来是正确的 (sk-)。")
            print("\n--- 正在测试 API 连通性 ---")
            
            # Test Qwen-Turbo (General)
            try:
                qwen_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
                headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
                payload = {"model": "qwen-turbo", "input": {"messages": [{"role": "user", "content": "hi"}]}}
                r = httpx.post(qwen_url, headers=headers, json=payload, timeout=10)
                print(f"Qwen-Turbo API 测试结果: 状态码 {r.status_code}")
                if r.status_code != 200:
                    print(f"错误信息: {r.text}")
            except Exception as e:
                print(f"Qwen API 测试失败: {e}")

            # Test Qwen3-TTS (Multimodal)
            try:
                mm_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
                headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
                payload = {
                    "model": "qwen3-tts-flash",
                    "input": {"text": "Hello, this is a test."},
                    "parameters": {"voice": "Cherry"}
                }
                r = httpx.post(mm_url, headers=headers, json=payload, timeout=10)
                print(f"Qwen3-TTS API 测试结果: 状态码 {r.status_code}")
                print(f"完整响应内容: {r.text}")
                if r.status_code == 200:
                    print("✅ 恭喜！你的 Key 拥有调用 Qwen3-TTS 的权限。")
            except Exception as e:
                print(f"Multimodal API 测试失败: {e}")

            # Test Qwen-VL-OCR (Multimodal)
            try:
                ocr_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
                payload = {
                    "model": "qwen-vl-ocr",
                    "input": {
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"image": "https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg"},
                                    {"text": "What is in this image?"}
                                ]
                            }
                        ]
                    }
                }
                r = httpx.post(ocr_url, headers=headers, json=payload, timeout=20)
                print(f"Qwen-VL-OCR API 测试结果: 状态码 {r.status_code}")
                if r.status_code == 200:
                    print("✅ 恭喜！你的 Key 拥有调用 Qwen-VL-OCR 的权限。")
                else:
                    print(f"OCR 错误信息: {r.text}")
            except Exception as e:
                print(f"OCR API 测试失败: {e}")
        else:
            print("🟡 Key 格式不明，请确保它是从阿里云 DashScope 控制台获取的。")

    print("--- 诊断结束 ---")

if __name__ == "__main__":
    diagnose()
