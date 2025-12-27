import httpx
from echo_tutor.config import get_settings
import base64
import os
from typing import Optional
import json

class ModelScopeClient:
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.modelscope_api_key
        
    async def ocr_image(self, image_path: str) -> dict:
        """
        Perform OCR on an image using DashScope Qwen-VL-OCR API
        """
        if not self.api_key:
            return {"text": "Error: API Key missing", "confidence": 0.0, "language": "en"}
            
        try:
            # Read and encode image
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")
            
            ext = os.path.splitext(image_path)[1].lower().replace(".", "")
            if ext == "jpg": ext = "jpeg"
            
            url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "qwen-vl-ocr",
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"image": f"data:image/{ext};base64,{image_data}"},
                                {"text": "Read all the text in the image exactly."}
                            ]
                        }
                    ]
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=60.0)
                response.raise_for_status()
                result = response.json()
                
                text = result.get("output", {}).get("choices", [{}])[0].get("message", {}).get("content", "")
                # If content is a list (multimodal response), extract text
                if isinstance(text, list):
                    text = " ".join([item.get("text", "") for item in text if "text" in item])
                
                return {
                    "text": text,
                    "confidence": 1.0,
                    "language": self._detect_language(text)
                }
        except Exception as e:
            print(f"OCR Error: {e}")
            return {
                "text": f"Error during OCR: {str(e)}",
                "confidence": 0.0,
                "language": "en"
            }
    
    async def text_to_speech(self, text: str, language: str = "zh-cn") -> bytes:
        """
        Convert text to speech using DashScope Qwen3-TTS-Flash API (Multimodal)
        """
        if not self.api_key:
            return b''
            
        try:
            # Using qwen3-tts-flash via multimodal endpoint
            model_name = "qwen3-tts-flash"
            url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model_name,
                "input": {
                    "text": text
                },
                "parameters": {
                    "voice": "Cherry" # Default voice
                }
            }
            
            if self.settings.debug:
                print(f"TTS Request: {text[:50]}...")
                
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=60.0)
                
                if self.settings.debug:
                    print(f"TTS Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Correct parsing for qwen3-tts-flash REST response
                    audio_info = result.get("output", {}).get("audio", {})
                    audio_url = audio_info.get("url")
                    
                    if audio_url and audio_url.startswith("http"):
                        if self.settings.debug:
                            print(f"TTS Audio URL: {audio_url}")
                        # Fetch audio from URL
                        async with httpx.AsyncClient() as audio_client:
                            audio_resp = await audio_client.get(audio_url)
                            return audio_resp.content
                    
                    print(f"TTS Error: Unexpected response format or missing URL: {result}")
                    return b''
                else:
                    print(f"TTS Error: HTTP {response.status_code} - {response.text}")
                    return b''
        except Exception as e:
            print(f"TTS Error in exception: {e}")
            return b''
    
    async def chat_with_qwen(self, messages: list) -> str:
        """
        Chat with Qwen LLM via ModelScope API
        """
        try:
            # Using DashScope API (Alibaba Cloud's API for Qwen)
            url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.settings.qwen_model,
                "input": {
                    "messages": messages
                },
                "parameters": {
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "max_tokens": 1500
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=30.0)
                response.raise_for_status()
                result = response.json()
                
            return result['output']['text']
        except Exception as e:
            print(f"Qwen API Error: {e}")
            # Fallback response for demo
            return "这是一个示例回答。请配置正确的 ModelScope API Key 以使用完整功能。"
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        # Check if contains Chinese characters
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                return "zh-cn"
        return "en"
