from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from echo_tutor.models.schemas import *
from echo_tutor.agents.graph import create_learning_graph
from echo_tutor.agents.tutor_agent import PronunciationTutorAgent
from echo_tutor.config import get_settings
import aiofiles
import uuid
import os
from pathlib import Path

router = APIRouter()
settings = get_settings()

# In-memory session storage (use Redis in production)
sessions = {}

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a document or image file
    """
    # Validate file size
    content = await file.read()
    if len(content) > settings.max_file_size:
        raise HTTPException(status_code=400, detail="File too large")
    
    # Determine file type
    file_ext = Path(file.filename).suffix.lower()
    if file_ext in ['.jpg', '.jpeg', '.png', '.bmp']:
        file_type = FileType.IMAGE
    elif file_ext in ['.txt', '.md']:
        file_type = FileType.DOCUMENT
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    # Save file
    file_id = str(uuid.uuid4())
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / f"{file_id}{file_ext}"
    
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    # Initialize LangGraph session
    graph = create_learning_graph()
    initial_state = {
        "messages": [],
        "file_path": str(file_path),
        "file_type": file_type.value,
        "extracted_text": "",
        "current_section": 0,
        "total_sections": 0,
        "user_action": "continue"
    }
    
    # Run the reader agent
    result = await graph.ainvoke(initial_state)
    
    # Store session
    sessions[file_id] = {
        "graph": graph,
        "state": result
    }
    
    return UploadResponse(
        file_id=file_id,
        file_type=file_type,
        message="File uploaded and processed successfully"
    )

@router.get("/session/{file_id}/current")
async def get_current_section(file_id: str):
    """
    Get the current learning section with audio and questions
    """
    if file_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[file_id]
    state = session["state"]
    
    # Get the last message which contains the tutoring data
    if not state["messages"]:
        raise HTTPException(status_code=400, detail="No content available")
    
    last_message = state["messages"][-1].content
    
    import json
    try:
        data = json.loads(last_message)
        return data
    except:
        return {"error": "Failed to parse session data"}

@router.post("/session/{file_id}/answer")
async def submit_answer(file_id: str, answer: UserAnswer):
    """
    Submit an answer to a question
    """
    if file_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[file_id]
    tutor = PronunciationTutorAgent()
    
    # Evaluate answer
    result = await tutor.evaluate_answer(
        session["state"],
        answer.answer,
        int(answer.question_id)
    )
    
    return FeedbackResponse(
        is_correct=result["is_correct"],
        explanation=result["explanation"],
        next_action="continue"
    )

@router.post("/session/{file_id}/next")
async def next_section(file_id: str):
    """
    Move to the next section
    """
    if file_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[file_id]
    state = session["state"]
    state["user_action"] = "next_section"
    
    # Increment section
    current = state.get("current_section", 0)
    state["current_section"] = current + 1
    
    # Continue the graph
    graph = session["graph"]
    result = await graph.ainvoke(state)
    
    session["state"] = result
    
    return {"message": "Moved to next section"}

