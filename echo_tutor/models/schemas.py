from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class FileType(str, Enum):
    DOCUMENT = "document"
    IMAGE = "image"

class UploadResponse(BaseModel):
    file_id: str
    file_type: FileType
    message: str

class OCRResult(BaseModel):
    text: str
    confidence: float
    language: Optional[str] = None

class TTSRequest(BaseModel):
    text: str
    language: str = "zh-cn"  # zh-cn or en

class TTSResponse(BaseModel):
    audio_url: str
    duration: float

class Question(BaseModel):
    question: str
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None

class TutorResponse(BaseModel):
    pronunciation_tips: str
    questions: List[Question]
    audio_url: Optional[str] = None

class UserAnswer(BaseModel):
    question_id: str
    answer: str

class FeedbackResponse(BaseModel):
    is_correct: bool
    explanation: str
    next_action: str  # "continue", "next_section", "end"
