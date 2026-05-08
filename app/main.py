from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import os

from app import storage, reader, ai, editor

app = FastAPI(title="i-love-docs")

# Static files and root route
BASE_DIR = Path(__file__).parent.parent.absolute()
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
async def get_index():
    return FileResponse(str(STATIC_DIR / "index.html"))

class ChatRequest(BaseModel):
    session_id: str
    message: str

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are accepted")
    
    storage.cleanup_old_files()
    session_id = storage.create_session()
    content = await file.read()
    storage.save_upload(session_id, content)
    
    return {"session_id": session_id, "filename": file.filename}

@app.post("/chat")
async def chat(request: ChatRequest):
    if not storage.file_exists(request.session_id):
        raise HTTPException(status_code=404, detail="Session not found. Please re-upload your file.")
    
    file_path = storage.get_file_path(request.session_id)
    document_text = reader.extract_content(str(file_path))
    
    instructions = ai.get_instructions(document_text, request.message)
    
    edited = False
    if instructions["action"] != "answer_only":
        success = editor.apply_edit(str(file_path), instructions)
        if success:
            edited = True
        else:
            instructions["explanation"] = "I tried to apply the edit but something went wrong with the document structure."
    
    return {
        "reply": instructions["explanation"],
        "edited": edited
    }

@app.get("/preview/{session_id}")
async def preview(session_id: str):
    if not storage.file_exists(session_id):
        raise HTTPException(status_code=404)
    
    file_path = storage.get_file_path(session_id)
    return FileResponse(
        str(file_path), 
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

@app.get("/download/{session_id}")
async def download(session_id: str):
    if not storage.file_exists(session_id):
        raise HTTPException(status_code=404)
    
    file_path = storage.get_file_path(session_id)
    return FileResponse(
        str(file_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=edited_document.docx"}
    )
