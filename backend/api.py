# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import asyncio
# from app import process_user_input
# from typing import Optional, Dict, Any

# app = FastAPI()

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],  # React app's address
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class UserInput(BaseModel):
#     query: str
#     session_data: Optional[Dict[str, Any]] = None

# @app.post("/chat")
# async def chat(user_input: UserInput):
#     try:
#         response = await process_user_input(user_input.query, user_input.session_data)
        
#         # If the response indicates we need more input
#         if isinstance(response, dict) and response.get("status") == "need_input":
#             return {
#                 "status": "need_input",
#                 "prompt": response["prompt"],
#                 "next_field": response["next_field"],
#                 "session_data": response.get("session_data", user_input.session_data or {})
#             }
        
#         # If the response is complete
#         if isinstance(response, dict):
#             return {
#                 "status": "complete",
#                 "response": response.get("data", response),
#                 "session_data": response.get("session_data", user_input.session_data or {})
#             }
        
#         # If response is not a dict (e.g., string)
#         return {
#             "status": "complete",
#             "response": response,
#             "session_data": user_input.session_data or {}
#         }
#     except Exception as e:
#         print(f"Error in chat endpoint: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000) 





# from fastapi import FastAPI, HTTPException, UploadFile, File
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import asyncio
# from app import process_user_input
# from typing import Optional, Dict, Any
# import shutil
# import os
# from pathlib import Path

# app = FastAPI()

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],  # React app's address
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Create uploads directory if it doesn't exist
# UPLOAD_DIR = Path("uploads")
# UPLOAD_DIR.mkdir(exist_ok=True)

# class UserInput(BaseModel):
#     query: str
#     session_data: Optional[Dict[str, Any]] = None

# @app.post("/upload-medical-records")
# async def upload_medical_records(files: list[UploadFile] = File(...)):
#     saved_files = []
#     try:
#         print('1')
#         for file in files:
#             file_path = UPLOAD_DIR / file.filename
#             with file_path.open("wb") as buffer:
#                 shutil.copyfileobj(file.file, buffer)
#             print(str(file_path))
#             saved_files.append(str(file_path))
#         print({"status": "success", "files": saved_files})
#         return {"status": "success", "files": saved_files}
#     except Exception as e:
#         # Clean up any files that were saved before the error
#         for file_path in saved_files:
#             try:
#                 os.remove(file_path)
#             except:
#                 pass
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/chat")
# async def chat(user_input: UserInput):
#     try:
#         response = await process_user_input(user_input.query, user_input.session_data)
#         print("API: Received response from process_user_input:", response)  # Debug log

#         if isinstance(response, dict) and response.get("status") == "need_input":
#             api_response = {
#                 **response,
#                 "session_data": response.get("session_data", user_input.session_data or {})
#             }
#             print("API: Sending response to frontend:", api_response)
#             return api_response

#         if isinstance(response, dict):
#             api_response = {
#                 "status": "complete",
#                 "response": response.get("data", response),
#                 "session_data": response.get("session_data", user_input.session_data or {})
#             }
#             print("API: Sending complete response:", api_response)  # Debug log
#             return api_response

#         return {
#             "status": "complete",
#             "response": response,
#             "session_data": user_input.session_data or {}
#         }
#     except Exception as e:
#         print(f"Error in chat endpoint: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000) 



from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from app import process_user_input
from typing import Optional, Dict, Any
import shutil
import os
from pathlib import Path

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app's address
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class UserInput(BaseModel):
    query: str
    session_data: Optional[Dict[str, Any]] = None

@app.post("/upload-medical-records")
async def upload_medical_records(files: list[UploadFile] = File(...)):
    saved_files = []
    try:
        for file in files:
            file_path = UPLOAD_DIR / file.filename
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_files.append(str(file_path))
        
        return {"status": "success", "files": saved_files}
    except Exception as e:
        # Clean up any files that were saved before the error
        for file_path in saved_files:
            try:
                os.remove(file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(user_input: UserInput):
    try:
        # print("API: Received request with query:", user_input.query)
        # print("API: Session data:", user_input.session_data)
        
        response = await process_user_input(user_input.query, user_input.session_data)
        # print("API: Received response from process_user_input:", response)  # Debug log
        
        # If we get a show_message status, pass it through
        if isinstance(response, dict) and response.get("status") == "show_message":
            # print("API: Passing through show_message:", response)  # Debug log
            return response
        
        # If the response indicates we need more input
        if isinstance(response, dict) and response.get("status") == "need_input":
            # Pass through all fields from the response
            api_response = {
                **response,  # Include all fields
                "session_data": response.get("session_data", user_input.session_data or {})
            }
            # print("API: Sending need_input response to frontend:", api_response)  # Debug log
            return api_response
        
        # If the response is complete
        if isinstance(response, dict):
            api_response = {
                "status": "complete",
                "response": response.get("data", response),
                "session_data": response.get("session_data", user_input.session_data or {})
            }
            # print("API: Sending complete response:", api_response)  # Debug log
            return api_response
        
        # If response is not a dict (e.g., string)
        api_response = {
            "status": "complete",
            "response": response,
            "session_data": user_input.session_data or {}
        }
        # print("API: Sending string response:", api_response)  # Debug log
        return api_response
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)