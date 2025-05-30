'''
Validates coverage, co-payments, and authorizations
'''
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from config import model_client
import asyncio
from typing import Dict, List, Any
from pprint import pprint
from monitoring import monitor_insurance_verification
from utils import input_once

INSURANCE_DATABASE = {
    "INS-123451": {
        "patient_name": "Haider Ali",
        "provider": "HealthCare Plus",
        "active": True,
        "coverage": {
            "general_consultation": {"copay": 20, "requires_authorization": False},
            "mri_scan": {"copay": 150, "requires_authorization": True}
        }
    },
    "INS-123452": {
        "patient_name": "Saim Ayub",
        "provider": "Wellness Shield",
        "active": True,
        "coverage": {
            "general_consultation": {"copay": 30, "requires_authorization": False}
        }
    }
}

PATIENT_INSURANCE_MAPPING = {
    "Haider Ali": "INS-123451",
    "Saim Ayub": "INS-123452"
}

async def get_insurance_id(session_data: dict = None) -> str:
    """Get insurance ID for a patient by name"""
    if session_data is None:
        session_data = {}

    if "name" not in session_data:
        return {
            "status": "need_input",
            "prompt": "Please enter your name:",
            "next_field": "name"
        }
    
    name = session_data["name"]
    insurance_id = PATIENT_INSURANCE_MAPPING.get(name)
    if not insurance_id:
        return {
            "status": "error",
            "message": f"No insurance found for patient {name}"
        }
    return insurance_id

async def verify_patient_coverage(session_data: dict = None) -> Dict:
    if session_data is None:
        session_data = {}

    # 1) patient name
    if "name" not in session_data:
        return {
            "status": "need_input",
            "prompt": "Please enter your name:",
            "next_field": "name"
        }

    # 2) service requested
    if "service" not in session_data:
        return {
            "status": "need_input",
            "prompt": "Enter the service to verify (e.g. general_consultation):",
            "next_field": "service"
        }

    # both present → do lookup
    name = session_data["name"]
    service = session_data["service"]

    insurance_id_result = await get_insurance_id(session_data)
    if isinstance(insurance_id_result, dict):
        # If we got a dict back, it's an error or need_input response
        return insurance_id_result

    insurance_id = insurance_id_result
    info = INSURANCE_DATABASE.get(insurance_id)
    if not info:
        return {
            "status": "error",
            "message": f"Insurance ID {insurance_id} not found in database"
        }

    covered = service in info["coverage"]
    coverage_details = info["coverage"].get(service, {})

    # trigger the monitoring/notification hook
    await monitor_insurance_verification({
        "patient_name": name,
        "insurance_found": True,
        "service_covered": covered,
        "service": service,
        "coverage_details": coverage_details
    })

    return {
        "status": "complete",
        "data": {
            "insurance_id": insurance_id,
            "provider": info["provider"],
            "service_covered": covered,
            "coverage_details": coverage_details
        }
    } 

# pprint(asyncio.run(verify_patient_coverage('Saim Ayub', 'general_consultation')))

insurance_verification_agent = AssistantAgent(
    name="InsuranceVerificationAgent",
    model_client=model_client,
    system_message="You are Insurance Verification Agent. Ask for patient name and service, verify coverage from the database, return a structured result with coverage details or clear error messages.",
    tools=[verify_patient_coverage, get_insurance_id],
)