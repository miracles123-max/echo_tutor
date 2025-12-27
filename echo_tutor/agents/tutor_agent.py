from typing import TypedDict
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from echo_tutor.services.modelscope_client import ModelScopeClient
from echo_tutor.agents.reader_agent import AgentState
from echo_tutor.config import get_settings
import json
import os

settings = get_settings()

class PronunciationTutorAgent:
    def __init__(self):
        self.client = ModelScopeClient()
    
    async def provide_pronunciation(self, state: AgentState) -> AgentState:
        """
        Generate pronunciation audio and create learning questions
        """
        text = state["extracted_text"]
        
        # Split text into manageable sections
        sections = [s.strip() for s in text.split('\n\n') if s.strip()]
        if not sections:
            sections = [s.strip() for s in text.split('。') if s.strip()]
        if not sections:
            sections = [text]
            
        current_idx = state.get("current_section", 0)
        
        if current_idx >= len(sections):
            state["messages"].append(
                AIMessage(content=json.dumps({
                    "completed": True,
                    "message": "All sections completed!"
                }))
            )
            return state
        
        current_text = sections[current_idx]
        
        # Generate TTS audio
        language = self.client._detect_language(current_text)
        audio_data = await self.client.text_to_speech(current_text, language)
        
        # Save audio file
        upload_dir = settings.upload_dir
        os.makedirs(upload_dir, exist_ok=True)
        audio_filename = f"audio_{current_idx}.wav"
        audio_path = os.path.join(upload_dir, audio_filename)
        
        if audio_data:
            with open(audio_path, 'wb') as f:
                f.write(audio_data)
        
        # Generate learning questions using Qwen
        questions = await self._generate_questions(current_text)
        
        state["messages"].append(
            AIMessage(content=json.dumps({
                "audio_path": audio_filename,
                "text": current_text,
                "questions": questions,
                "section": f"{current_idx + 1}/{len(sections)}",
                "completed": False
            }))
        )
        
        return state
    
    async def _generate_questions(self, text: str) -> list:
        """
        Use Qwen to generate comprehension questions
        """
        system_prompt = """你是一位语言学习导师。根据给定的文本段落，生成2-3个问题来帮助学生理解和练习内容。

对于每个问题，请提供：
1. 问题文本
2. 3-4个选项（如适用）
3. 正确答案
4. 简短解释

请以JSON格式返回，格式如下：
[
  {
    "question": "问题内容",
    "options": ["选项A", "选项B", "选项C", "选项D"],
    "correct_answer": "选项A",
    "explanation": "解释为什么这是正确答案"
  }
]
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请为以下文本生成学习问题：\n\n{text}"}
        ]
        
        try:
            response = await self.client.chat_with_qwen(messages)
            
            # Try to parse JSON response
            # Clean up the response if it contains markdown code blocks
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            questions = json.loads(cleaned_response)
            return questions
        except Exception as e:
            print(f"Question generation error: {e}")
            # Fallback questions
            return [
                {
                    "question": "这段文字的主要内容是什么？",
                    "options": ["选项A", "选项B", "选项C", "选项D"],
                    "correct_answer": "选项A",
                    "explanation": "这段文字主要讨论了..."
                },
                {
                    "question": "文中提到的关键信息是？",
                    "options": ["信息1", "信息2", "信息3", "信息4"],
                    "correct_answer": "信息1",
                    "explanation": "根据文本内容..."
                }
            ]
    
    async def evaluate_answer(self, state: AgentState, user_answer: str, question_id: int) -> dict:
        """
        Evaluate user's answer using Qwen
        """
        messages = state.get("messages", [])
        
        # Get the question context from previous messages
        last_message = messages[-1].content if messages else "{}"
        
        try:
            question_data = json.loads(last_message)
            questions = question_data.get("questions", [])
            
            if question_id >= len(questions):
                return {"is_correct": False, "explanation": "Invalid question ID"}
            
            question = questions[question_id]
            
            # Use Qwen to evaluate
            eval_messages = [
                {
                    "role": "system",
                    "content": "你是一位耐心的语言导师。评估学生的答案并提供建设性的反馈。"
                },
                {
                    "role": "user",
                    "content": f"问题：{question['question']}\n正确答案：{question['correct_answer']}\n学生的答案：{user_answer}\n\n学生答对了吗？请提供反馈。"
                }
            ]
            
            feedback = await self.client.chat_with_qwen(eval_messages)
            
            is_correct = user_answer.lower().strip() == question['correct_answer'].lower().strip()
            
            return {
                "is_correct": is_correct,
                "explanation": feedback
            }
        except Exception as e:
            print(f"Answer evaluation error: {e}")
            return {
                "is_correct": False,
                "explanation": "评估答案时出错，请重试。"
            }
