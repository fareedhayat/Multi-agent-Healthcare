from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from config import model_client
from typing import Dict, List
import asyncio
from datetime import datetime, timedelta
from clinical_recommendation import generate_clinical_recommendations
from monitoring import monitor_patient_case
from patient_intake import collect_medical_history, get_current_situation
import json

async def review_patient_case(session_data: dict = None) -> Dict:
    if session_data is None:
        session_data = {}
    try:
        print('review patient case')
        
        # Get medical history first
        medical_history = await collect_medical_history(session_data)
        if medical_history.get("status") == "need_input":
            return medical_history
        medical_history_data = medical_history.get("data")
        
        # Then get symptoms
        current_symptoms = await get_current_situation(session_data)
        if current_symptoms.get("status") == "need_input":
            return current_symptoms
        symptoms_data = current_symptoms.get("data", {}).get("symptoms", [])

        if medical_history_data and symptoms_data:
            print("Medical History Data:", medical_history_data)
            print("Symptoms Data:", symptoms_data)

            try:
                # Check if we have valid medical history structure
                if not isinstance(medical_history_data, list) or not medical_history_data:
                    medical_history_data = [{
                        "Patient info": {
                            "patient_name": "Unknown Patient"
                        },
                        "Medical Info": {}
                    }]
                
                # Ensure we have patient info structure
                if "Patient info" not in medical_history_data[0]:
                    medical_history_data[0]["Patient info"] = {"patient_name": "Unknown Patient"}
                
                patient_name = medical_history_data[0]['Patient info'].get('patient_name', 'Unknown Patient')
                recommendations = await generate_clinical_recommendations(
                    medical_history=medical_history_data,
                    symptoms=symptoms_data
                )

                diagnosis = await confirm_diagnosis(recommendations["possible_diagnoses"])
                treatment_plan = await create_treatment_plan(recommendations["treatment_options"])
                diagnostic_test = recommendations["diagnostic_tests"]
                follow_up = await schedule_follow_up(diagnosis)

                results = {
                    "diagnosis": diagnosis,
                    "treatment_plan": treatment_plan,
                    "diagnostic_test": diagnostic_test,
                    "follow_up": follow_up
                }

                monitoring_status = await monitor_patient_case(
                    patient_name=patient_name,
                    clinical_data=results
                )

                print(monitoring_status)
                print(results)

            except Exception as e:
                return {"error": f"Failed to process medical data: {str(e)}"}

    except Exception as e:
        return {"error": f"Case review failed: {str(e)}"}

async def confirm_diagnosis(possible_diagnoses: List[str]) -> str:
    """Doctor selects most likely diagnosis"""
    # In this case returning the first one
    return possible_diagnoses[0] if possible_diagnoses else "Unknown"

async def create_treatment_plan(treatment_options: List[str]) -> List[str]:
    """Doctor finalizes treatment plan"""
    # Returns the first two
    return [
        f"PRIMARY: {treatment_options[0]}",
        # f"SECONDARY: {treatment_options[1]}" if len(treatment_options) > 1 else ""
    ]

async def schedule_follow_up(diagnosis: str) -> str:
    """Determine follow-up timing based on condition"""
    follow_up_days = {
        "acute": 7,
        "chronic": 30,
        "preventive": 90
    }.get(diagnosis.lower(), 14)
    
    follow_up_date = (datetime.now() + timedelta(days=follow_up_days)).strftime("%Y-%m-%d")
    return f"Follow-up in {follow_up_days} days ({follow_up_date})"

doctor_agent = AssistantAgent(
    name="DoctorAgent",
    model_client=model_client,
    system_message="You are DoctorAgent. Review patient history and symptoms, suggest a primary diagnosis, create a treatment plan, and schedule follow‑ups. Report errors clearly and use an empathetic, concise tone.",
    tools=[review_patient_case],
    # reflect_on_tool_use=True
)