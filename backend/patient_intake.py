'''
Collects medical history, symptoms, and consent before visits
''' 
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from config import model_client
from typing import List, Dict
from analyze_documents import analyze_previous_records
import asyncio
from utils import input_once
# from executor import executor 


async def collect_basic_info(session_data: dict = None) -> Dict:
    if session_data is None:
        session_data = {}

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

    if "documents" not in session_data:
        return {
            "status": "need_input",
            "prompt": "Enter paths to medical-record documents (comma separated):",
            "next_field": "documents"
        }

    paths = [
        p.strip() 
        for p in session_data["documents"].split(",") 
        if p.strip()
    ]
    history = []
    for idx, document in enumerate(paths, start=1):
        patient_info, medical_info = await analyze_previous_records(document)
        history.append({
            "Document": f"Document {idx}",
            "Patient info": patient_info,
            "Medical Info": medical_info
        })

    return {
        "status": "complete",
        "data": history
    }


async def get_current_situation(session_data: dict = None) -> Dict:
    if session_data is None:
        session_data = {}

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