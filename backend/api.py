from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from app import process_user_input
from typing import Optional, Dict, Any

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app's address
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserInput(BaseModel):
    query: str
    session_data: Optional[Dict[str, Any]] = None

@app.post("/chat")
async def chat(user_input: UserInput):
    try:
        response = await process_user_input(user_input.query, user_input.session_data)
        
        # If the response indicates we need more input
        if isinstance(response, dict) and response.get("status") == "need_input":
            return {
                "status": "need_input",
                "prompt": response["prompt"],
                "next_field": response["next_field"],
                "session_data": response.get("session_data", user_input.session_data or {})
            }
        
        # If the response is complete
        if isinstance(response, dict):
            return {
                "status": "complete",
                "response": response.get("data", response),
                "session_data": response.get("session_data", user_input.session_data or {})
            }
        
        # If response is not a dict (e.g., string)
        return {
            "status": "complete",
            "response": response,
            "session_data": user_input.session_data or {}
        }
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 