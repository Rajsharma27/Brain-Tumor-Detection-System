from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import uuid
import httpx
from src.modules.rag_chatbot import get_chatbot
from src.database.db import db
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Chatbot Service")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions: Dict[str, dict] = {}


class SessionInit(BaseModel):
    session_id: Optional[str] = None
    patient_name: Optional[str] = None
    diagnosis: Optional[str] = None
    report_content: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    symptoms: Optional[str] = None
    description: Optional[str] = None
    precautions: Optional[str] = None
    things_to_remember: Optional[str] = None
    confidence: Optional[float] = None


class ChatMessage(BaseModel):
    session_id: str
    user_message: str


class ChatResponse(BaseModel):
    session_id: str
    user_message: str
    bot_response: str


@app.on_event("startup")
async def startup_event():
    print(" Chatbot service initialized")


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "chatbot",
        "sessions_active": len(sessions)
    }


def restore_session_from_db(session_id: str):
    """Restore a session from database to memory if it exists."""
    if session_id in sessions:
        return  # Already loaded
    
    
    session_db = db.get_session(session_id)
    if not session_db:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found in database")
    
    
    report_lines = []
    if session_db.get("patient_name"):
        report_lines.append(f"Patient Name: {session_db.get('patient_name')}")
    if session_db.get("age"):
        report_lines.append(f"Age: {session_db.get('age')}")
    if session_db.get("gender"):
        report_lines.append(f"Gender: {session_db.get('gender')}")
    if session_db.get("symptoms"):
        report_lines.append(f"Symptoms: {session_db.get('symptoms')}")
    if session_db.get("diagnosis"):
        report_lines.append(f"Diagnosis: {session_db.get('diagnosis')}")
    if session_db.get("confidence"):
        report_lines.append(f"Confidence Score: {session_db.get('confidence') * 100:.2f}%")
    if session_db.get("description"):
        report_lines.append(f"Clinical Description:\n{session_db.get('description')}\n")
    if session_db.get("precautions"):
        report_lines.append(f"Recommended Precautions:\n{session_db.get('precautions')}\n")
    if session_db.get("things_to_remember"):
        report_lines.append(f"Things to Remember:\n{session_db.get('things_to_remember')}\n")
    
    final_report_content = "\n".join(report_lines)
    
    # Recreate chatbot with report content
    chatbot = get_chatbot(report_content=final_report_content)
    
    # Restore session to memory
    sessions[session_id] = {
        "patient_name": session_db.get("patient_name", "Unknown"),
        "diagnosis": session_db.get("diagnosis", "Not provided"),
        "report_content": final_report_content,
        "age": session_db.get("age"),
        "gender": session_db.get("gender"),
        "symptoms": session_db.get("symptoms"),
        "description": session_db.get("description"),
        "precautions": session_db.get("precautions"),
        "things_to_remember": session_db.get("things_to_remember"),
        "confidence": session_db.get("confidence"),
        "report_id": session_db.get("report_id"),
        "chatbot": chatbot
    }
    
    print(f"✅ Session {session_id} restored from database")


@app.post("/initialize-session")
async def initialize_session(session_data: SessionInit):
    try:
        # Generate session_id and report_id
        session_id = session_data.session_id or str(uuid.uuid4())
        report_id = str(uuid.uuid4())
        
        # Initialize content fields
        description = session_data.description
        precautions = session_data.precautions
        things_to_remember = session_data.things_to_remember
        
        # If report content fields are not provided, generate them from AI
        if not (description and precautions and things_to_remember):
            print(f"📝 Generating report content from AI for patient: {session_data.patient_name}")
            try:
                # Call Report Generator API to generate AI content
                async with httpx.AsyncClient(timeout=60.0) as client:
                    print(f" Calling http://localhost:8001/generate-content")
                    report_response = await client.post(
                        "http://localhost:8001/generate-content",
                        data={
                            "prediction": session_data.diagnosis or "Not provided",
                            "name": session_data.patient_name or "Unknown",
                            "age": session_data.age or 0,
                            "gender": session_data.gender or "Not specified",
                            "symptoms": session_data.symptoms or "Not specified",
                            "confidence": session_data.confidence or 0.0
                        }
                    )
                
                print(f"Report API Response Status: {report_response.status_code}")
                
                if report_response.status_code == 200:
                    report_data = report_response.json()
                    description = report_data.get("description", "")
                    precautions = report_data.get("precautions", "")
                    things_to_remember = report_data.get("things_to_remember", "")
                    print(f"✅ AI-generated report content received successfully")
                    print(f"   Description: {len(description)} chars")
                    print(f"   Precautions: {len(precautions)} chars")
                    print(f"   Things to Remember: {len(things_to_remember)} chars")
                else:
                    print(f" Report generation API returned status {report_response.status_code}")
                    print(f"   Response: {report_response.text}")
                    description = session_data.description or ""
                    precautions = session_data.precautions or ""
                    things_to_remember = session_data.things_to_remember or ""
            except httpx.ConnectError as e:
                print(f"❌ Could not connect to Report Generator API at http://localhost:8001: {e}")
                print(f"   Make sure Report Generator service is running on port 8001")
                description = session_data.description or ""
                precautions = session_data.precautions or ""
                things_to_remember = session_data.things_to_remember or ""
            except Exception as e:
                print(f"❌ Error calling Report Generator API: {e}")
                description = session_data.description or ""
                precautions = session_data.precautions or ""
                things_to_remember = session_data.things_to_remember or ""
        else:
            print(f"ℹ Using provided report content (not generating from AI)")
        
        # Build comprehensive report content from all fields
        report_lines = []
        
        if session_data.patient_name:
            report_lines.append(f"Patient Name: {session_data.patient_name}")
        if session_data.age:
            report_lines.append(f"Age: {session_data.age}")
        if session_data.gender:
            report_lines.append(f"Gender: {session_data.gender}")
        if session_data.symptoms:
            report_lines.append(f"Symptoms: {session_data.symptoms}")
        if session_data.diagnosis:
            report_lines.append(f"Diagnosis: {session_data.diagnosis}")
        if session_data.confidence:
            report_lines.append(f"Confidence Score: {session_data.confidence * 100:.2f}%")
        
        report_lines.append("\n--- AI GENERATED REPORT ---\n")
        
        if description:
            report_lines.append(f"Clinical Description:\n{description}\n")
        if precautions:
            report_lines.append(f"Recommended Precautions:\n{precautions}\n")
        if things_to_remember:
            report_lines.append(f"Things to Remember:\n{things_to_remember}\n")
        
        # Use provided report_content if given, otherwise build from fields
        final_report_content = session_data.report_content or "\n".join(report_lines)
        
        # Save report to database with AI-generated content
        db_report_data = {
            "report_id": report_id,
            "patient_name": session_data.patient_name,
            "age": session_data.age,
            "gender": session_data.gender,
            "symptoms": session_data.symptoms,
            "diagnosis": session_data.diagnosis,
            "confidence": session_data.confidence,
            "description": description,
            "precautions": precautions,
            "things_to_remember": things_to_remember
        }
        db.save_report(db_report_data)
        
        # Create chat session in database
        db.create_session(session_id, report_id, db_report_data)
        
        # Get chatbot instance with report content if provided
        if final_report_content.strip():
            chatbot = get_chatbot(report_content=final_report_content)
        else:
            chatbot = get_chatbot()
        
        # Store session metadata in memory for quick access
        sessions[session_id] = {
            "patient_name": session_data.patient_name or "Unknown",
            "diagnosis": session_data.diagnosis or "Not provided",
            "report_content": final_report_content,
            "age": session_data.age,
            "gender": session_data.gender,
            "symptoms": session_data.symptoms,
            "description": description,
            "precautions": precautions,
            "things_to_remember": things_to_remember,
            "confidence": session_data.confidence,
            "report_id": report_id,
            "chatbot": chatbot
        }
        
        print(f"✅ Report saved: {report_id}")
        print(f"✅ Session created: {session_id}")
        
        return {
            "success": True,
            "session_id": session_id,
            "report_id": report_id,
            "message": "Session initialized successfully with AI-generated report"
        }
    except Exception as e:
        print(f"Error initializing session: {e}")
        raise HTTPException(status_code=500, detail=f"Error initializing session: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
async def chat(message_data: ChatMessage):
    try:
        session_id = message_data.session_id
        user_message = message_data.user_message
        
        # Restore session from database if not in memory
        if session_id not in sessions:
            restore_session_from_db(session_id)
        
        # Get chatbot for this session
        chatbot = sessions[session_id].get("chatbot")
        if not chatbot:
            raise HTTPException(status_code=500, detail="Chatbot not initialized for this session")
        
        # Save user message to database
        db.add_message(session_id, "user", user_message)
        
        # Get response from chatbot
        bot_response = chatbot.answer_question(user_message)
        
        # Save bot response to database
        db.add_message(session_id, "bot", bot_response)
        
        return ChatResponse(
            session_id=session_id,
            user_message=user_message,
            bot_response=bot_response
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@app.post("/update-report")
async def update_report(request: Request):
    try:
        data = await request.json()
        session_id = data.get("session_id")
        report_content = data.get("report_content", "")
        
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Update chatbot with new report content
        chatbot = sessions[session_id].get("chatbot")
        if chatbot:
            chatbot.update_report_content(report_content)
            sessions[session_id]["report_content"] = report_content
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Report content updated successfully"
        }
    except Exception as e:
        print(f"Error updating report: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating report: {str(e)}")


@app.post("/clear-history")
async def clear_history(request: Request):
    try:
        data = await request.json()
        session_id = data.get("session_id")
        
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Clear chatbot memory
        chatbot = sessions[session_id].get("chatbot")
        if chatbot:
            chatbot.clear_memory()
        
        # Clear messages from database
        db.clear_messages(session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Conversation history cleared"
        }
    except Exception as e:
        print(f"Error clearing history: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing history: {str(e)}")


@app.get("/sessions")
async def list_sessions():
    db_sessions = db.get_all_sessions()
    return {
        "sessions": [
            {
                "session_id": s["session_id"],
                "patient_name": s["patient_name"],
                "diagnosis": s["diagnosis"],
                "age": s["age"],
                "gender": s["gender"],
                "symptoms": s["symptoms"],
                "created_at": s["created_at"],
                "updated_at": s["updated_at"],
                "active": s["session_id"] in sessions
            }
            for s in db_sessions
        ],
        "total": len(db_sessions),
        "active": len(sessions)
    }


@app.get("/sessions/{session_id}")
async def get_session_detail(session_id: str):
    """Get detailed information about a specific session from database."""
    session_db = db.get_session(session_id)
    if not session_db:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    # Get messages for this session
    messages = db.get_messages(session_id)
    
    return {
        "session_id": session_id,
        "patient_name": session_db.get("patient_name"),
        "diagnosis": session_db.get("diagnosis"),
        "age": session_db.get("age"),
        "gender": session_db.get("gender"),
        "symptoms": session_db.get("symptoms"),
        "description": session_db.get("description"),
        "precautions": session_db.get("precautions"),
        "things_to_remember": session_db.get("things_to_remember"),
        "confidence": session_db.get("confidence"),
        "report_id": session_db.get("report_id"),
        "created_at": session_db.get("created_at"),
        "updated_at": session_db.get("updated_at"),
        "messages": messages,
        "message_count": len(messages),
        "active": session_id in sessions
    }


@app.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: str):
    """Get all messages for a session."""
    if not db.get_session(session_id):
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    messages = db.get_messages(session_id)
    return {
        "session_id": session_id,
        "messages": messages,
        "total": len(messages)
    }


@app.get("/reports/{report_id}")
async def get_report_detail(report_id: str):
    """Get detailed information about a report."""
    report = db.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    
    return report


@app.get("/reports")
async def list_reports():
    """List all reports from database."""
    reports = db.get_all_reports()
    return {
        "reports": reports,
        "total": len(reports)
    }


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and all associated messages."""
    session_db = db.get_session(session_id)
    if not session_db:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    # Delete from database
    db.delete_session(session_id)
    
    # Remove from memory if exists
    if session_id in sessions:
        del sessions[session_id]
    
    return {
        "success": True,
        "session_id": session_id,
        "message": "Session deleted successfully from database"
    }


@app.delete("/reports/{report_id}")
async def delete_report(report_id: str):
    """Delete a report from database."""
    report = db.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    
    db.delete_report(report_id)
    
    return {
        "success": True,
        "report_id": report_id,
        "message": "Report deleted successfully from database"
    }


@app.get("/stats")
async def get_stats():
    """Get database statistics."""
    stats = db.get_database_stats()
    return {
        "database_stats": stats,
        "active_sessions": len(sessions),
        "timestamp": str(__import__('datetime').datetime.now())
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
