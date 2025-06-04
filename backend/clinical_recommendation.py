# '''
# Assists doctors with diagnostics and treatment plans
# '''
# from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
# from autogen_core.models import SystemMessage
# from config import model_client
# from typing import Dict, List
# import asyncio
# import re
# import json, ast

# # Create a knowledge base like this one from the symptoms and history
# # integrate LLM for this
# # def create_medical_kb()
# # use the medical history and the symptoms to create this
# # MEDICAL_KB = {
# #     'disease 1': {
# #         "diagnostic_criteria": ["criteria 1", "criteria 2", "criteria 3"],
# #         "treatments": ["treatment 1", "treatment 2", "treatment 3"],
# #         "tests": ["test 1", "test 2"],
# #         "urgency": "low/moderate/high"
# #     },
# #     'disease 2': {
# #         "diagnostic_criteria": ["criteria 1", "criteria 2", "criteria 3"],
# #         "treatments": ["treatment 1", "treatment 2", "treatment 3"],
# #         "tests": ["test 1", "test 2"],
# #         "urgency": "low/moderate/high"
# #     }
# # }

# # MEDICAL_KB = {
# #     "hypertension": {
# #         "diagnostic_criteria": ["bp > 140/90", "headache", "vision changes"],
# #         "treatments": ["lifestyle changes", "ACE inhibitors", "calcium blockers"],
# #         "tests": ["blood pressure monitoring"],
# #         "urgency": "moderate"
# #     },
# #     "diabetes": {
# #         "diagnostic_criteria": ["fasting glucose > 126", "thirst", "fatigue"],
# #         "treatments": ["metformin", "insulin", "diet control"],
# #         "tests": ["HbA1c test"],
# #         "urgency": "high"
# #     }
# # }

# async def generate_medical_kb(medical_history: Dict, symptoms: List[str]) -> Dict:
#     prompt = f"""
#     You are a medical assistant. Based on the following medical history and symptoms, generate a medical knowledge base as valid JSON.

#     Medical History: {medical_history}
#     Symptoms: {symptoms}

#     Respond ONLY with a JSON object in the following format (no explanation):

#     {{
#     "Disease A": {{
#         "diagnostic_criteria": ["symptom1", "symptom2"],
#         "treatments": ["treatment1", "treatment2"],
#         "tests": ["test1", "test2"],
#         "urgency": "low"
#     }},
#     "Disease B": {{
#         "diagnostic_criteria": ["symptom3"],
#         "treatments": ["treatment3"],
#         "tests": ["test3"],
#         "urgency": "moderate"
#     }}
#     }}

#     Limit to 2 diseases only. Use short keywords (not full sentences) for criteria, treatments, and tests.
#     """
#     response = await model_client.create([SystemMessage(content=prompt)])
#     content = response.content.strip()
#     print("Raw content from model:\n", content)
#     cleaned_content = re.sub(r"^```json|```$", "", content.strip(), flags=re.MULTILINE).strip()


#     try:
#         kb = json.loads(cleaned_content)
#     except json.JSONDecodeError as e:
#         raise ValueError(f"Failed to parse model output. Cleaned content:\n{cleaned_content}\nError: {str(e)}")
    
#     return kb

# def normalize(text):
#     return text.strip().lower().replace(" ", "_")


# async def generate_clinical_recommendations(medical_history: Dict, symptoms: List[str], session_data: dict = None) -> Dict:
#     if session_data is None:
#         session_data = {}

    
#     if "generate_clinical_recommendations_message" not in session_data:
#         return {
#             "status": "show_message",
#             "message": "Clinical Recommendation Agent: Starting to generate clinical recommendation according to the symptoms.",
#             "next_field": "generate_clinical_recommendations_message"
#         }
    
#     try:
#         possible_diagnoses = []
#         diagnostic_tests = []
#         MEDICAL_KB = await generate_medical_kb(medical_history, symptoms)
#         if MEDICAL_KB:
#             if "generate_medical_kb_message" not in session_data:
#                 return {
#                     "status": "show_message",
#                     "message": "Clinical Recommendation Agent: Starting to generate Medical Knowledge Base according to the symptoms.",
#                     "next_field": "generate_medical_kb_message"
#                 }
#         print(MEDICAL_KB)
#         for condition, data in MEDICAL_KB.items():
#             symptom_matches = [
#                 s for s in symptoms if normalize(s) in [normalize(c) for c in data["diagnostic_criteria"]]
#             ]
#             if len(symptom_matches) >= 1:
#                 possible_diagnoses.append(condition)
#                 diagnostic_tests.extend(data.get("tests", []))


#         treatment_options = []
#         for diagnosis in possible_diagnoses:
#             treatment_options.extend(MEDICAL_KB[diagnosis]["treatments"])
        
#         result = {
#             "possible_diagnoses": possible_diagnoses,
#             "treatment_options": list(set(treatment_options)),
#             "diagnostic_tests": list(set(diagnostic_tests)),
#             "confidence_score": "60%" # get confidence score from the generation of medical knowledge base
#         }
#         print(result)
#         return result
        
#     except Exception as e:
#         return {"error": f"Recommendation generation failed: {str(e)}"}

# # def get_diagnostic_tests(condition: str, history: Dict) -> List[str]:
# #     """Safely get diagnostic tests for a condition"""
# #     try:
# #         condition_data = MEDICAL_KB.get(condition, {})
# #         if not isinstance(condition_data, dict):
# #             return []
            
# #         tests = condition_data.get("tests", [])
# #         return tests if isinstance(tests, list) else []
        
# #     except Exception:
# #         return []
    

# clinical_recommendation_agent = AssistantAgent(
#     name="ClinicalRecommendationAgent",
#     model_client=model_client,
#     system_message="You are Clinical Recommendation Agent. Generate a two-disease JSON knowledge base (criteria, tests, treatments, urgency), match symptoms to diagnoses, list treatment options and tests, include a confidence score, and return only JSON.",
#     tools=[generate_medical_kb, generate_clinical_recommendations]
# ) 



'''
Assists doctors with diagnostics and treatment plans
'''
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_core.models import SystemMessage
from config import model_client
from typing import Dict, List
import asyncio
import re
import json, ast

# Create a knowledge base like this one from the symptoms and history
# integrate LLM for this
# def create_medical_kb()
# use the medical history and the symptoms to create this
# MEDICAL_KB = {
#     'disease 1': {
#         "diagnostic_criteria": ["criteria 1", "criteria 2", "criteria 3"],
#         "treatments": ["treatment 1", "treatment 2", "treatment 3"],
#         "tests": ["test 1", "test 2"],
#         "urgency": "low/moderate/high"
#     },
#     'disease 2': {
#         "diagnostic_criteria": ["criteria 1", "criteria 2", "criteria 3"],
#         "treatments": ["treatment 1", "treatment 2", "treatment 3"],
#         "tests": ["test 1", "test 2"],
#         "urgency": "low/moderate/high"
#     }
# }

# MEDICAL_KB = {
#     "hypertension": {
#         "diagnostic_criteria": ["bp > 140/90", "headache", "vision changes"],
#         "treatments": ["lifestyle changes", "ACE inhibitors", "calcium blockers"],
#         "tests": ["blood pressure monitoring"],
#         "urgency": "moderate"
#     },
#     "diabetes": {
#         "diagnostic_criteria": ["fasting glucose > 126", "thirst", "fatigue"],
#         "treatments": ["metformin", "insulin", "diet control"],
#         "tests": ["HbA1c test"],
#         "urgency": "high"
#     }
# }

async def generate_medical_kb(medical_history: Dict, symptoms: List[str]) -> Dict:
    prompt = f"""
    You are a medical assistant. Based on the following medical history and symptoms, generate a medical knowledge base as valid JSON.

    Medical History: {medical_history}
    Symptoms: {symptoms}

    Respond ONLY with a JSON object in the following format (no explanation):

    {{
    "Disease A": {{
        "diagnostic_criteria": ["symptom1", "symptom2"],
        "treatments": ["treatment1", "treatment2"],
        "tests": ["test1", "test2"],
        "urgency": "low"
    }},
    "Disease B": {{
        "diagnostic_criteria": ["symptom3"],
        "treatments": ["treatment3"],
        "tests": ["test3"],
        "urgency": "moderate"
    }}
    }}

    Limit to 2 diseases only. Use short keywords (not full sentences) for criteria, treatments, and tests.
    """
    response = await model_client.create([SystemMessage(content=prompt)])
    content = response.content.strip()
    print("Raw content from model:\n", content)
    cleaned_content = re.sub(r"^```json|```$", "", content.strip(), flags=re.MULTILINE).strip()


    try:
        kb = json.loads(cleaned_content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse model output. Cleaned content:\n{cleaned_content}\nError: {str(e)}")
    
    return kb

def normalize(text):
    return text.strip().lower().replace(" ", "_")


async def generate_clinical_recommendations(session_data: dict = None) -> Dict:
    if session_data is None:
        session_data = {}

    if "generate_recommendations_message" not in session_data:
        return {
            "status": "show_message",
            "message": "Clinical Recommendation Agent: Analyzing medical history and symptoms to generate recommendations",
            "next_field": "generate_recommendations_message"
        }

    medical_history = session_data.get("medical_history", {})
    symptoms = session_data.get("symptoms", [])

    try:
        possible_diagnoses = []
        diagnostic_tests = []
        MEDICAL_KB = await generate_medical_kb(medical_history, symptoms)
        print(MEDICAL_KB)
        for condition, data in MEDICAL_KB.items():
            symptom_matches = [
                s for s in symptoms if normalize(s) in [normalize(c) for c in data["diagnostic_criteria"]]
            ]
            if len(symptom_matches) >= 1:
                possible_diagnoses.append(condition)
                diagnostic_tests.extend(data.get("tests", []))


        treatment_options = []
        for diagnosis in possible_diagnoses:
            treatment_options.extend(MEDICAL_KB[diagnosis]["treatments"])
        
        result = {
            "possible_diagnoses": possible_diagnoses,
            "treatment_options": list(set(treatment_options)),
            "diagnostic_tests": list(set(diagnostic_tests)),
            "confidence_score": "60%" # get confidence score from the generation of medical knowledge base
        }
        print(result)
        return result
        
    except Exception as e:
        return {"error": f"Recommendation generation failed: {str(e)}"}

# def get_diagnostic_tests(condition: str, history: Dict) -> List[str]:
#     """Safely get diagnostic tests for a condition"""
#     try:
#         condition_data = MEDICAL_KB.get(condition, {})
#         if not isinstance(condition_data, dict):
#             return []
            
#         tests = condition_data.get("tests", [])
#         return tests if isinstance(tests, list) else []
        
#     except Exception:
#         return []
    

clinical_recommendation_agent = AssistantAgent(
    name="ClinicalRecommendationAgent",
    model_client=model_client,
    system_message="You are Clinical Recommendation Agent. Generate a two-disease JSON knowledge base (criteria, tests, treatments, urgency), match symptoms to diagnoses, list treatment options and tests, include a confidence score, and return only JSON.",
    tools=[generate_medical_kb, generate_clinical_recommendations]
)