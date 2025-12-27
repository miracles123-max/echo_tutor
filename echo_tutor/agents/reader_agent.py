from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage, AIMessage
from echo_tutor.services.modelscope_client import ModelScopeClient
import operator

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    file_path: str
    extracted_text: str
    file_type: str
    current_section: int
    total_sections: int
    user_action: str

class DocumentReaderAgent:
    def __init__(self):
        self.client = ModelScopeClient()
    
    async def process_document(self, state: AgentState) -> AgentState:
        """
        Process document or image to extract text
        """
        file_path = state["file_path"]
        file_type = state["file_type"]
        
        if file_type == "image":
            # Perform OCR
            ocr_result = await self.client.ocr_image(file_path)
            extracted_text = ocr_result["text"]
            
            state["messages"].append(
                AIMessage(content=f"OCR completed. Extracted {len(extracted_text)} characters.")
            )
        else:
            # For text documents, read directly
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    extracted_text = f.read()
                
                state["messages"].append(
                    AIMessage(content=f"Document read. Total {len(extracted_text)} characters.")
                )
            except Exception as e:
                extracted_text = f"Error reading file: {e}"
                state["messages"].append(
                    AIMessage(content=f"Error: {e}")
                )
        
        state["extracted_text"] = extracted_text
        
        # Split into sections (simple split by paragraphs or sentences)
        sections = [s.strip() for s in extracted_text.split('\n\n') if s.strip()]
        if not sections:
            # If no paragraphs, split by sentences
            sections = [s.strip() for s in extracted_text.split('。') if s.strip()]
        if not sections:
            sections = [extracted_text]
        
        state["total_sections"] = len(sections)
        if "current_section" not in state or state["current_section"] is None:
            state["current_section"] = 0
        
        return state
