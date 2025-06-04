# from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
# from config import model_client
# from typing import Dict, List
# import asyncio
# from datetime import datetime, timedelta
# from clinical_recommendation import generate_clinical_recommendations
# from monitoring import monitor_patient_case
# from patient_intake import collect_medical_history, get_current_situation
# import json

# async def review_patient_case(session_data: dict = None) -> Dict:
#     if session_data is None:
#         session_data = {}
#     try:
#         if "review_patient_case_message" not in session_data:
#             return {
#                 "status": "show_message",
#                 "message": "Doctor Agent: Starting to review symptoms and medical history.",
#                 "next_field": "review_patient_case_message"
#             }

#         # Get medical history first
#         medical_history = await collect_medical_history(session_data)
#         if medical_history.get("status") == "need_input":
#             return medical_history
#         medical_history_data = medical_history.get("data")
        
#         # Then get symptoms
#         current_symptoms = await get_current_situation(session_data)
#         if current_symptoms.get("status") == "need_input":
#             return current_symptoms
#         symptoms_data = current_symptoms.get("data", {}).get("symptoms", [])

#         if medical_history_data and symptoms_data:
#             print("Medical History Data:", medical_history_data)
#             print("Symptoms Data:", symptoms_data)

#             try:
#                 # Check if we have valid medical history structure
#                 if not isinstance(medical_history_data, list) or not medical_history_data:
#                     medical_history_data = [{
#                         "Patient info": {
#                             "patient_name": "Unknown Patient"
#                         },
#                         "Medical Info": {}
#                     }]
                
#                 # Ensure we have patient info structure
#                 if "Patient info" not in medical_history_data[0]:
#                     medical_history_data[0]["Patient info"] = {"patient_name": "Unknown Patient"}
                
#                 patient_name = medical_history_data[0]['Patient info'].get('patient_name', 'Unknown Patient')
#                 recommendations = await generate_clinical_recommendations(
#                     medical_history=medical_history_data,
#                     symptoms=symptoms_data,
#                     session_data=session_data
#                 )

#                 diagnosis = await confirm_diagnosis(recommendations["possible_diagnoses"], session_data=session_data)
#                 treatment_plan = await create_treatment_plan(recommendations["treatment_options"], session_data=session_data)
#                 diagnostic_test = recommendations["diagnostic_tests"]
#                 follow_up = await schedule_follow_up(diagnosis, session_data=session_data)

#                 results = {
#                     "diagnosis": diagnosis,
#                     "treatment_plan": treatment_plan,
#                     "diagnostic_test": diagnostic_test,
#                     "follow_up": follow_up
#                 }

#                 monitoring_status = await monitor_patient_case(
#                     patient_name=patient_name,
#                     clinical_data=results, 
#                     session_data=session_data
#                 )

#                 print(monitoring_status)
#                 print(results)

#             except Exception as e:
#                 return {"error": f"Failed to process medical data: {str(e)}"}

#     except Exception as e:
#         return {"error": f"Case review failed: {str(e)}"}

# async def confirm_diagnosis(possible_diagnoses: List[str], session_data: dict = None) -> str:
#     if session_data is None:
#         session_data = {}
    
#     if "confirm_diagnosis_message" not in session_data:
#             return {
#                 "status": "show_message",
#                 "message": "Doctor Agent: diagnosing the disease.",
#                 "next_field": "confirm_diagnosis_message"
#             }

#     return possible_diagnoses[0] if possible_diagnoses else "Unknown"

# async def create_treatment_plan(treatment_options: List[str], session_data: dict = None) -> List[str]:
#     if session_data is None:
#         session_data = {}
    
#     if "create_treatment_plan_message" not in session_data:
#             return {
#                 "status": "show_message",
#                 "message": "Doctor Agent: Adding treatment plans to the review report.",
#                 "next_field": "create_treatment_plan_message"
#             }

#     return [
#         f"PRIMARY: {treatment_options[0]}",
#         # f"SECONDARY: {treatment_options[1]}" if len(treatment_options) > 1 else ""
#     ]

# async def schedule_follow_up(diagnosis: str, session_data: dict = None) -> str:
#     if session_data is None:
#         session_data = {}
    
#     if "create_treatment_plan_message" not in session_data:
#             return {
#                 "status": "show_message",
#                 "message": "Doctor Agent: Adding a follow up date.",
#                 "next_field": "create_treatment_plan_message"
#             }
#     """Determine follow-up timing based on condition"""
#     follow_up_days = {
#         "acute": 7,
#         "chronic": 30,
#         "preventive": 90
#     }.get(diagnosis.lower(), 14)
    
#     follow_up_date = (datetime.now() + timedelta(days=follow_up_days)).strftime("%Y-%m-%d")
#     return f"Follow-up in {follow_up_days} days ({follow_up_date})"

# doctor_agent = AssistantAgent(
#     name="DoctorAgent",
#     model_client=model_client,
#     system_message="You are DoctorAgent. Review patient history and symptoms, suggest a primary diagnosis, create a treatment plan, and schedule follow‑ups. Report errors clearly and use an empathetic, concise tone.",
#     tools=[review_patient_case],
#     # reflect_on_tool_use=True
# ) 




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

    print(f"starting data: {session_data}")

    # Initial message
    if "review_case_message" not in session_data:
        return {
            "status": "show_message",
            "message": "Doctor Agent: Starting patient case review",
            "next_field": "review_case_message"
        }
    print(f"After message data: {session_data}")

    try:
        print('review patient case')
        
        # First check if we need basic patient info
        if "name" not in session_data:
            return {
                "status": "need_input",
                "prompt": "Please enter your name:",
                "next_field": "name"
            }
        
        patient_name = session_data['name']
        
        print(f"After Name data: {session_data}")

        # Get medical history first if not already in session
        if "medical_history_data" not in session_data:
            if "processed_medical_history" in session_data:
                session_data["medical_history_data"] = session_data["processed_medical_history"]
            else:
                medical_history = await collect_medical_history(session_data)
                if medical_history.get("status") in ["show_message", "need_input"]:
                    print(f"review_patient_case: Returning status from collect_medical_history: {medical_history.get('status')}")
                    return medical_history
                session_data["medical_history_data"] = medical_history.get("data")
                print(f"review_patient_case: collect_medical_history returned complete. session_data keys after update: {session_data.keys()}")
        
        medical_history_data = session_data.get("medical_history_data")
        print(f"review_patient_case: Before symptoms check. session_data keys: {session_data.keys()}")
        print(f"review_patient_case: session_data['symptoms'] is {session_data.get('symptoms')}")

        if "symptoms" not in session_data:
            symptoms = await get_current_situation(session_data)   # ← add await!
            if isinstance(symptoms, dict) and symptoms.get("status") in ["show_message", "need_input"]:
                print(f"review_patient_case: Returning status from get_current_situation: {symptoms.get('status')}")
                return symptoms
            session_data["symptoms"] = symptoms.get("data", symptoms)

        # Get symptoms from session data - do not ask again
        symptoms_data = []
        if isinstance(session_data.get("symptoms"), str):
            symptoms_data = [s.strip() for s in session_data["symptoms"].split(",")]
        elif isinstance(session_data.get("symptoms"), list):
            symptoms_data = session_data["symptoms"]

        print(f"After symptoms data: {session_data}")


        if medical_history_data and symptoms_data:
            print("Medical History Data:", medical_history_data)
            print("Symptoms Data:", symptoms_data)

            try:
                # Check if we have valid medical history structure
                # if not isinstance(medical_history_data, list) or not medical_history_data:
                #     medical_history_data = [{
                #         "Patient info": {
                #             "patient_name": session_data.get("name", "Unknown Patient")
                #         },
                #         "Medical Info": {}
                #     }]
                
                # # Ensure we have patient info structure
                # if "Patient info" not in medical_history_data[0]:
                #     medical_history_data[0]["Patient info"] = {"patient_name": session_data.get("name", "Unknown Patient")}
                
                # patient_name = medical_history_data[0]['Patient info'].get('patient_name', session_data.get("name", "Unknown Patient"))
                
                # Update session data with required info
                session_data["medical_history"] = medical_history_data
                session_data["symptoms"] = symptoms_data
                

                recommendations = await generate_clinical_recommendations(session_data)
                if isinstance(recommendations, dict) and recommendations.get("status") == "show_message":
                    return recommendations
                
                print(f"after recommendation data: {session_data}")


                diagnosis = await confirm_diagnosis(session_data=session_data, possible_diagnoses=recommendations["possible_diagnoses"])
                if isinstance(diagnosis, dict) and diagnosis.get("status") == "show_message":
                    return diagnosis
                treatment_plan = await create_treatment_plan(session_data=session_data, treatment_options=recommendations["treatment_options"])
                if isinstance(treatment_plan, dict) and treatment_plan.get("status") == "show_message":
                    return treatment_plan
                diagnostic_test = recommendations["diagnostic_tests"]
                follow_up = await schedule_follow_up(session_data=session_data, diagnosis=diagnosis)
                if isinstance(follow_up, dict) and follow_up.get("status") == "show_message":
                    return follow_up

                results = {
                    "diagnosis": diagnosis,
                    "treatment_plan": treatment_plan,
                    "diagnostic_test": diagnostic_test,
                    "follow_up": follow_up
                }

                monitoring_result = await monitor_patient_case(
                    session_data=session_data,
                    patient_name=patient_name,
                    clinical_data=results
                )
                
                if isinstance(monitoring_result, dict) and monitoring_result.get("status") == "show_message":
                    return monitoring_result

                print(monitoring_result)
                print(results)

                return {
                    "status": "complete",
                    "data": results
                }

            except Exception as e:
                print(f"Error processing medical data: {str(e)}")
                return {"error": f"Failed to process medical data: {str(e)}"}

    except Exception as e:
        print(f"Error in case review: {str(e)}")
        return {"error": f"Case review failed: {str(e)}"}


async def confirm_diagnosis(session_data: dict = None, possible_diagnoses: List[str] = None) -> str:
    if session_data is None:
        session_data = {}

    if "confirm_diagnosis_message" not in session_data:
        return {
            "status": "show_message",
            "message": "Doctor Agent: Confirming diagnosis based on symptoms and medical history",
            "next_field": "confirm_diagnosis_message"
        }

    """Doctor selects most likely diagnosis"""
    # In this case returning the first one
    return possible_diagnoses[0] if possible_diagnoses else "Unknown"

async def create_treatment_plan(session_data: dict = None, treatment_options: List[str] = None) -> List[str]:
    if session_data is None:
        session_data = {}

    if "create_treatment_message" not in session_data:
        return {
            "status": "show_message",
            "message": "Doctor Agent: Creating personalized treatment plan",
            "next_field": "create_treatment_message"
        }

    """Doctor finalizes treatment plan"""
    # Returns the first two
    return [
        f"PRIMARY: {treatment_options[0]}",
        # f"SECONDARY: {treatment_options[1]}" if len(treatment_options) > 1 else ""
    ]

async def schedule_follow_up(session_data: dict = None, diagnosis: str = None) -> str:
    if session_data is None:
        session_data = {}

    if "schedule_followup_message" not in session_data:
        return {
            "status": "show_message",
            "message": "Doctor Agent: Scheduling follow-up appointment based on diagnosis",
            "next_field": "schedule_followup_message"
        }

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