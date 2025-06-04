# '''
# Collects medical history, symptoms, and consent before visits
# ''' 
# from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
# from config import model_client
# from typing import List, Dict
# from analyze_documents import analyze_previous_records
# import asyncio
# from utils import input_once
# # from executor import executor 


# async def collect_basic_info(session_data: dict = None) -> Dict:
#     if session_data is None:
#         session_data = {}

#     if "name" not in session_data:
#         return {
#             "status": "need_input",
#             "prompt": "Please enter your name:",
#             "next_field": "name"
#         }

#     if "age" not in session_data:
#         return {
#             "status": "need_input",
#             "prompt": "Please enter your age:",
#             "next_field": "age"
#         }

#     if "address" not in session_data:
#         return {
#             "status": "need_input",
#             "prompt": "Please enter your address:",
#             "next_field": "address"
#         }

#     return {
#         "status": "complete",
#         "data": {
#             "name": session_data["name"],
#             "age": session_data["age"],
#             "address": session_data["address"]
#         }
#     }

# async def collect_medical_history(session_data: dict = None) -> Dict:
#     if session_data is None:
#         session_data = {}

#     if "documents" not in session_data:
#         return {
#             "status": "need_input",
#             "prompt": "Enter paths to medical-record documents (comma separated):",
#             "next_field": "documents"
#         }

#     paths = [
#         p.strip() 
#         for p in session_data["documents"].split(",") 
#         if p.strip()
#     ]
#     history = []
#     for idx, document in enumerate(paths, start=1):
#         patient_info, medical_info = await analyze_previous_records(document)
#         history.append({
#             "Document": f"Document {idx}",
#             "Patient info": patient_info,
#             "Medical Info": medical_info
#         })

#     return {
#         "status": "complete",
#         "data": history
#     }


# async def get_current_situation(session_data: dict = None) -> Dict:
#     if session_data is None:
#         session_data = {}

#     if "symptoms" not in session_data:
#         session_data["symptoms"] = []
#         return {
#             "status": "need_input",
#             "prompt": "Please list all your symptoms (separate with commas):",
#             "next_field": "symptoms"
#         }

#     # Handle both string and list inputs
#     symptoms = session_data["symptoms"]
#     if isinstance(symptoms, str):
#         symptoms = [s.strip() for s in symptoms.split(",") if s.strip()]
#     elif isinstance(symptoms, list):
#         symptoms = [s.strip() for s in symptoms if s.strip()]
#     else:
#         symptoms = []

#     print("Current symptoms:", symptoms)

#     if symptoms:
#         session_data["symptoms"] = symptoms
#         return {
#             "status": "complete",
#             "data": {
#                 "symptoms": symptoms
#             }
#         }

#     return {
#         "status": "need_input",
#         "prompt": "Please enter at least one symptom (separate multiple with commas):",
#         "next_field": "symptoms"
#     }

# patient_intake_agent = AssistantAgent(
#     name="PatientIntakeAgent",
#     model_client=model_client,
#     system_message="You are Patient IntakeAgent. Collect basic patient info (name, age, address) and prior records paths, then gather current symptoms until the user stops. Cache symptoms to avoid repeats.",
#     tools=[collect_basic_info, get_current_situation, collect_medical_history]
# )





# '''
# Collects medical history, symptoms, and consent before visits
# ''' 
# from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
# from config import model_client
# from typing import List, Dict
# from analyze_documents import analyze_previous_records
# import asyncio
# from utils import input_once
# from pathlib import Path
# # from executor import executor 


# async def collect_basic_info(session_data: dict = None) -> Dict:
#     if session_data is None:
#         session_data = {} 

#     if "collect_basic_info_message" not in session_data:
#         return {
#             "status": "show_message",
#             "message": "Patient Intake Agent: Collecting your basic information",
#             "next_field": "collect_basic_info_message"
#         }

#     if "name" not in session_data:
#         return {
#             "status": "need_input",
#             "prompt": "Please enter your name:",
#             "next_field": "name"
#         }

#     if "age" not in session_data:
#         return {
#             "status": "need_input",
#             "prompt": "Please enter your age:",
#             "next_field": "age"
#         }

#     if "address" not in session_data:
#         return {
#             "status": "need_input",
#             "prompt": "Please enter your address:",
#             "next_field": "address"
#         }

#     return {
#         "status": "complete",
#         "data": {
#             "name": session_data["name"],
#             "age": session_data["age"],
#             "address": session_data["address"]
#         }
#     }

# async def collect_medical_history(session_data: dict = None) -> Dict:
#     if session_data is None:
#         session_data = {}

#     print(f"Starting collect_medical_history with session data: {session_data}")  # Debug log

#     # Check if we already have processed documents
#     if "processed_medical_history" in session_data:
#         print("Found existing processed medical history")  # Debug log
#         return {
#             "status": "complete",
#             "data": session_data["processed_medical_history"]
#         }

#     # Special handling for file upload completion
#     if session_data.get("file_upload_complete"):
#         print(f"Processing uploaded files from session data: {session_data}")  # Debug log
        
#         # Get file paths from documents field
#         paths = session_data.get('documents', [])
#         if isinstance(paths, str):
#             paths = [p.strip() for p in paths.split(",") if p.strip() and p not in ["PROCESS_UPLOADED_FILES"]]
#         elif isinstance(paths, list):
#             paths = [p for p in paths if p and p not in ["PROCESS_UPLOADED_FILES"]]
#         else:
#             paths = []

#         print(f"Processing medical records from paths: {paths}")  # Debug log

#         if not paths:
#             print("No valid paths provided")  # Debug log
#             return {
#                 "status": "need_input",
#                 "prompt": "No valid medical records were found. Please upload your medical record documents.",
#                 "next_field": "documents",
#                 "requiresFileUpload": True,
#                 "type": "file_upload"
#             }

#         history = []
#         for idx, document in enumerate(paths, start=1):
#             document_path = Path(document)
#             print(f"Processing document {idx}: {document_path} (exists: {document_path.exists()})")  # Debug log
            
#             if not document_path.exists():
#                 print(f"Document does not exist: {document_path}")  # Debug log
#                 continue
                
#             try:
#                 print(f"Analyzing document {idx} with analyze_previous_records")  # Debug log
#                 patient_info, medical_info = await analyze_previous_records(str(document_path))
#                 history.append({
#                     "Document": f"Document {idx}",
#                     "Patient info": patient_info,
#                     "Medical Info": medical_info
#                 })
#                 print(f"Successfully processed document {idx}: {patient_info}, {medical_info}")  # Debug log
#             except Exception as e:
#                 print(f"Error processing document {idx}: {str(e)}")  # Debug log
#                 continue

#         if not history:
#             print("No documents were successfully processed")  # Debug log
#             return {
#                 "status": "need_input",
#                 "prompt": "No valid medical records were found. Please upload your medical record documents.",
#                 "next_field": "documents",
#                 "requiresFileUpload": True,
#                 "type": "file_upload"
#             }

#         print(f"Successfully processed {len(history)} documents")  # Debug log
        
#         # Store the processed history in session data
#         session_data["processed_medical_history"] = history
#         print(f"Updated session data with processed history: {session_data}")  # Debug log
        
#         # Move to collecting symptoms
#         return {
#             "status": "need_input",
#             "prompt": "Please list all your symptoms (separate with commas):",
#             "next_field": "symptoms",
#             "session_data": session_data
#         }

#     # Initial request for file upload
#     if "documents" not in session_data or not session_data.get("file_upload_complete"):
#         print("Requesting initial file upload")  # Debug log
#         return {
#             "status": "need_input",
#             "prompt": "Please upload your medical record documents",
#             "next_field": "documents",
#             "requiresFileUpload": True,
#             "type": "file_upload"
#         }

#     # If we have symptoms but no processed history, process the documents
#     if "symptoms" in session_data and not session_data.get("processed_medical_history"):
#         print("Have symptoms but no processed history, processing documents")  # Debug log
#         return await collect_medical_history(session_data)

#     print(f"Unexpected state in collect_medical_history: {session_data}")  # Debug log
#     return {
#         "status": "need_input",
#         "prompt": "Please upload your medical record documents",
#         "next_field": "documents",
#         "requiresFileUpload": True,
#         "type": "file_upload"
#     }

# async def get_current_situation(session_data: dict = None) -> Dict:
#     if session_data is None:
#         session_data = {}

#     if "get_current_situation_message" not in session_data:
#         return {
#             "status": "show_message",
#             "message": "Patient Intake Agent: Getting to know your current situation.",
#             "next_field": "get_current_situation_message"
#         }
    
#     if "symptoms" not in session_data:
#         session_data["symptoms"] = []
#         return {
#             "status": "need_input",
#             "prompt": "Please list all your symptoms (separate with commas):",
#             "next_field": "symptoms"
#         }

#     # Handle both string and list inputs
#     symptoms = session_data["symptoms"]
#     if isinstance(symptoms, str):
#         symptoms = [s.strip() for s in symptoms.split(",") if s.strip()]
#     elif isinstance(symptoms, list):
#         symptoms = [s.strip() for s in symptoms if s.strip()]
#     else:
#         symptoms = []

#     print("Current symptoms:", symptoms)

#     if symptoms:
#         session_data["symptoms"] = symptoms
#         return {
#             "status": "complete",
#             "data": {
#                 "symptoms": symptoms
#             }
#         }

#     return {
#         "status": "need_input",
#         "prompt": "Please enter at least one symptom (separate multiple with commas):",
#         "next_field": "symptoms"
#     }

# patient_intake_agent = AssistantAgent(
#     name="PatientIntakeAgent",
#     model_client=model_client,
#     system_message="You are Patient IntakeAgent. Collect basic patient info (name, age, address) and prior records paths, then gather current symptoms until the user stops. Cache symptoms to avoid repeats.",
#     tools=[collect_basic_info, get_current_situation, collect_medical_history]
# ) 






'''
Collects medical history, symptoms, and consent before visits
''' 
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from config import model_client
from typing import List, Dict
from analyze_documents import analyze_previous_records
import asyncio
from utils import input_once
from pathlib import Path
# from executor import executor 


async def collect_basic_info(session_data: dict = None) -> Dict:
    if session_data is None:
        session_data = {}

    if "collect_basic_info_message" not in session_data:
        return {
            "status": "show_message",
            "message": "Patient Intake Agent: Collecting your basic information",
            "next_field": "collect_basic_info_message"
        }

    if "name" not in session_data:
        return {
            "status": "need_input",
            "prompt": "Please enter your name:",
            "next_field": "name"
        }

    if "age" not in session_data:
        return {
            "status": "need_input",
            "prompt": "Please enter your age:",
            "next_field": "age"
        }

    if "address" not in session_data:
        return {
            "status": "need_input",
            "prompt": "Please enter your address:",
            "next_field": "address"
        }

    return {
        "status": "complete",
        "data": {
            "name": session_data["name"],
            "age": session_data["age"],
            "address": session_data["address"]
        }
    }

async def collect_medical_history(session_data: dict = None) -> Dict:
    if session_data is None:
        session_data = {}

    if "collect_history_message" not in session_data:
        return {
            "status": "show_message",
            "message": "Patient Intake Agent: Collecting your medical history",
            "next_field": "collect_history_message"
        }

    print(f"Starting collect_medical_history with session data: {session_data}")  # Debug log

    # Check if we already have processed documents
    if "processed_medical_history" in session_data:
        print("Found existing processed medical history")  # Debug log
        return {
            "status": "complete",
            "data": session_data["processed_medical_history"]
        }

    # Special handling for file upload completion
    if session_data.get("file_upload_complete"):
        print(f"Processing uploaded files from session data: {session_data}")  # Debug log
        
        # Get file paths from documents field
        paths = session_data.get('documents', [])
        if isinstance(paths, str):
            paths = [p.strip() for p in paths.split(",") if p.strip() and p not in ["PROCESS_UPLOADED_FILES"]]
        elif isinstance(paths, list):
            paths = [p for p in paths if p and p not in ["PROCESS_UPLOADED_FILES"]]
        else:
            paths = []

        print(f"Processing medical records from paths: {paths}")  # Debug log

        if not paths:
            print("No valid paths provided")  # Debug log
            return {
                "status": "need_input",
                "prompt": "No valid medical records were found. Please upload your medical record documents.",
                "next_field": "documents",
                "requiresFileUpload": True,
                "type": "file_upload"
            }

        history = []
        for idx, document in enumerate(paths, start=1):
            document_path = Path(document)
            print(f"Processing document {idx}: {document_path} (exists: {document_path.exists()})")  # Debug log
            
            if not document_path.exists():
                print(f"Document does not exist: {document_path}")  # Debug log
                continue
                
            try:
                print(f"Analyzing document {idx} with analyze_previous_records")  # Debug log
                patient_info, medical_info = await analyze_previous_records(str(document_path))
                history.append({
                    "Document": f"Document {idx}",
                    "Patient info": patient_info,
                    "Medical Info": medical_info
                })
                print(f"Successfully processed document {idx}: {patient_info}, {medical_info}")  # Debug log
            except Exception as e:
                print(f"Error processing document {idx}: {str(e)}")  # Debug log
                continue

        if not history:
            print("No documents were successfully processed")  # Debug log
            return {
                "status": "need_input",
                "prompt": "No valid medical records were found. Please upload your medical record documents.",
                "next_field": "documents",
                "requiresFileUpload": True,
                "type": "file_upload"
            }

        print(f"Successfully processed {len(history)} documents")  # Debug log
        
        # Store the processed history in session data
        session_data["processed_medical_history"] = history
        print(f"Updated session data with processed history: {session_data}")  # Debug log
        
        # Move to collecting symptoms
        return {
            "status": "complete",
            "data": {
            "processed_medical_history": session_data["processed_medical_history"],
        }
        }

    # Initial request for file upload
    if "documents" not in session_data or not session_data.get("file_upload_complete"):
        print("Requesting initial file upload")  # Debug log
        return {
            "status": "need_input",
            "prompt": "Please upload your medical record documents",
            "next_field": "documents",
            "requiresFileUpload": True,
            "type": "file_upload"
        }

    # If we have symptoms but no processed history, process the documents
    if "symptoms" in session_data and not session_data.get("processed_medical_history"):
        print("Have symptoms but no processed history, processing documents")  # Debug log
        return await collect_medical_history(session_data)

    print(f"Unexpected state in collect_medical_history: {session_data}")  # Debug log
    return {
        "status": "need_input",
        "prompt": "Please upload your medical record documents",
        "next_field": "documents",
        "requiresFileUpload": True,
        "type": "file_upload"
    }


async def get_current_situation(session_data: dict = None) -> Dict:
    if session_data is None:
        session_data = {}
    print(f"get_current_situation: Start with session_data keys: {session_data.keys()}")

    if "get_symptoms_message" not in session_data:
        return {
            "status": "show_message",
            "message": "Patient Intake Agent: Collecting your current symptoms",
            "next_field": "get_symptoms_message"
        }

    if "symptoms" not in session_data:
        session_data["symptoms"] = []
        return {
            "status": "need_input",
            "prompt": "Please list all your symptoms (separate with commas):",
            "next_field": "symptoms"
        }

    # Handle both string and list inputs
    symptoms = session_data["symptoms"]
    if isinstance(symptoms, str):
        symptoms = [s.strip() for s in symptoms.split(",") if s.strip()]
    elif isinstance(symptoms, list):
        symptoms = [s.strip() for s in symptoms if s.strip()]
    else:
        symptoms = []

    print("Current symptoms:", symptoms)

    if symptoms:
        session_data["symptoms"] = symptoms
        return {
            "status": "complete",
            "data": {
                "symptoms": symptoms
            }
        }

    return {
        "status": "need_input",
        "prompt": "Please enter at least one symptom (separate multiple with commas):",
        "next_field": "symptoms"
    }

patient_intake_agent = AssistantAgent(
    name="PatientIntakeAgent",
    model_client=model_client,
    system_message="You are Patient IntakeAgent. Collect basic patient info (name, age, address) and prior records paths, then gather current symptoms until the user stops. Cache symptoms to avoid repeats.",
    tools=[collect_basic_info, get_current_situation, collect_medical_history]
)