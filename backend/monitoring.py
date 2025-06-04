# '''
# Tracks follow-ups and provide details to notificaiton agent.
# '''
# from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
# from config import model_client 
# from helper import get_event_details
# from notification import notify_appointment, notify_clinical_review, notify_insurance_status
# from datetime import datetime, timedelta
# import asyncio
# from typing import Any
# from tool_decorator import label_tool

# @label_tool("Monitoring appointment status")
# # async def monitor_appointments(appointment_id: str, action: str, session_data: dict = None, **kwargs: Any) -> str:
#     # if session_data is None:
#     #     session_data = {}

#     # if "monitor_appointments_message" not in session_data:
#     #         return {
#     #             "status": "show_message",
#     #             "message": "Monitoring Agent: Monitoring the appointment process, you will be notified soon.",
#     #             "next_field": "monitor_appointments_message"
#     #         } 

# async def monitor_appointments(appointment_id: str, action: str, **kwargs: Any) -> str:
#     try:
#         # current_details = await get_event_details(appointment_id)
#         # if not current_details:
#         #     return "Error: Could not retrieve appointment details"

#         messages = []
        
#         if action == "created":
#             current_details = kwargs.get("original_details")
#             messages.append(await handle_new_appointment(current_details))
            
#         elif action == "rescheduled":
#             current_details = await get_event_details(appointment_id)
#             original_details = kwargs.get("original_details")
#             if original_details:
#                 messages.append(await handle_reschedule(current_details, original_details))
            
#         elif action == "deleted":
#             current_details = kwargs.get("current_details")
#             if current_details:
#                 messages.append(await handle_deletion(current_details))

#         if messages:
#             print(current_details)
#             session_data = kwargs.get("session_data")
#             await notify_appointment(current_details, messages, session_data=session_data)
#         # print(notification["message"])
#         print(messages)
#         print(f"Monitoring completed for {appointment_id}")
    
#     except Exception as e:
#         print(f"Monitoring error: {str(e)}")
#         return "Monitoring failed"

# async def monitor_patient_case(patient_name: str, clinical_data: dict, session_data: dict = None):
#     if session_data is None:
#         session_data = {}

#     if "monitor_patient_case_message" not in session_data:
#             return {
#                 "status": "show_message",
#                 "message": "Monitoring Agent: Monitoring the review process, you will be notified soon.",
#                 "next_field": "monitor_patient_case_message"
#             }

#     message = format_clinical_summary(clinical_data)
#     notification_status = await notify_clinical_review(
#         patient_name=patient_name,
#         message_params=message, 
#         session_data=session_data
#     )

#     return notification_status

# async def monitor_insurance_verification(insurance_data: dict, session_data: dict = None):
#     if session_data is None:
#         session_data = {}

#     if "monitor_insurance_verification_message" not in session_data:
#             return {
#                 "status": "show_message",
#                 "message": "Monitoring Agent: Monitoring the insurance verification process, you will be notified soon.",
#                 "next_field": "monitor_insurance_verification_message"
#             }
#     try:
#         patient_name = insurance_data['patient_name']
#         notification_type = "INSURANCE_VERIFIED" if insurance_data.get("insurance_found") else "INSURANCE_NOT_FOUND"
        
#         if insurance_data.get("insurance_found"):
#             response = await notify_insurance_status(
#                 patient_name=patient_name,
#                 insurance_data=insurance_data,
#                 message_type=notification_type, 
#                 session_data=session_data
#             )
#         else:
#             response = await notify_insurance_status(
#                 patient_name=patient_name,
#                 insurance_data=insurance_data,
#                 message_type=notification_type, 
#                 session_data=session_data
#             )

#         print(f"Notification Status: {response.get('status', 'unknown')}")
#         if response.get("status") == "failure":
#             print(f"Email Error: {response.get('message')}")

#     except Exception as e:
#         print(f"Insurance monitoring failed: {str(e)}")
#         # await notify_insurance_status(
#         #     insurance_data={"error": str(e)},
#         #     message_type="INSURANCE_ERROR"
#         # )

# def format_clinical_summary(clinical_data: dict) -> dict:
#     return {
#         "diagnosis": clinical_data.get("diagnosis", "Pending diagnosis"),
#         "treatment_plan": "\n- ".join(clinical_data.get("treatment_plan", ["No treatment plan"])),
#         "diagnostic_tests": ", ".join(clinical_data.get("diagnostic_test", ["No tests required"])),
#         "follow_up_date": clinical_data.get("follow_up", "No follow-up scheduled"),
#         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
#     }

# async def handle_new_appointment(details: dict) -> str:
#     return (
#         "New appointment confirmed:\n"
#         f"Date: {details.get('start', 'N/A')}\n"
#     )

# async def handle_reschedule(current_details: dict, original_details: dict) -> str:
#     return (
#         "Appointment rescheduled:\n"
#         f"Original: {original_details.get('start', 'N/A')}\n"
#         f"New Time: {current_details.get('start', 'N/A')}\n"
#         f"Changes: {find_changes(original_details, current_details)}"
#     )

# async def handle_deletion(previous_details: dict) -> str:
#     return (
#         "Appointment cancelled:\n"
#         f"Original Date: {previous_details.get('start', 'N/A')}\n"
#     )

# def find_changes(old: dict, new: dict) -> str:
#     changes = []
#     for key in ['start']:
#         old_val = old.get(key, 'N/A')
#         new_val = new.get(key, 'N/A')
#         if old_val != new_val:
#             changes.append(f"{key}: {old_val} → {new_val}")
#     return "\n".join(changes) if changes else "No significant changes"

# monitoring_agent = AssistantAgent(
#     name="MonitoringAgent",
#     model_client=model_client,
#     system_message="You are Monitoring Agent. Watch for appointment, patient-case, and insurance status changes; format succinct update summaries; and trigger notifications.",
#     tools=[monitor_appointments, monitor_patient_case, monitor_insurance_verification],
#     reflect_on_tool_use=True
# ) 


'''
Tracks follow-ups and provide details to notificaiton agent.
'''
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from config import model_client 
from helper import get_event_details
from notification import notify_appointment, notify_clinical_review, notify_insurance_status
from datetime import datetime, timedelta
import asyncio
from typing import Any
from tool_decorator import label_tool

@label_tool("Monitoring appointment status")
async def monitor_appointments(
    session_data: dict = None,
    appointment_id: str = None, 
    action: str = None,
    **kwargs: Any
) -> str:
    if session_data is None:
        session_data = {}

    if "monitor_appointments_message" not in session_data:
        return {
            "status": "show_message",
            "message": "Monitoring Agent: Tracking appointment status changes",
            "next_field": "monitor_appointments_message"
        }

    try:
        messages = []
        
        if action == "created":
            current_details = kwargs.get("original_details")
            messages.append(await handle_new_appointment(current_details))
            
        elif action == "rescheduled":
            current_details = await get_event_details(appointment_id)
            original_details = kwargs.get("original_details")
            if original_details:
                messages.append(await handle_reschedule(current_details, original_details))
            
        elif action == "deleted":
            current_details = kwargs.get("current_details")
            if current_details:
                messages.append(await handle_deletion(current_details))

        if messages:
            print(current_details)
            notification_result = await notify_appointment(
                session_data=session_data,
                current_details=current_details,
                messages=messages
            )
            if isinstance(notification_result, dict) and notification_result.get("status") == "show_message":
                return notification_result
        
        print(messages)
        print(f"Monitoring completed for {appointment_id}")
    
    except Exception as e:
        print(f"Monitoring error: {str(e)}")
        return "Monitoring failed"

async def monitor_patient_case(session_data: dict = None, patient_name: str = None, clinical_data: dict = None):
    if session_data is None:
        session_data = {}

    if "monitor_patient_message" not in session_data:
        return {
            "status": "show_message",
            "message": "Monitoring Agent: Tracking patient case updates",
            "next_field": "monitor_patient_message"
        }

    print('monitor patient case function')
    message = format_clinical_summary(clinical_data)
    notification_result = await notify_clinical_review(
        session_data=session_data,
        patient_name=patient_name,
        message_params=message
    )
    
    if isinstance(notification_result, dict) and notification_result.get("status") == "show_message":
        return notification_result

    return notification_result

async def monitor_insurance_verification(session_data: dict = None, insurance_data: dict = None):
    if session_data is None:
        session_data = {}

    if "monitor_insurance_message" not in session_data:
        return {
            "status": "show_message",
            "message": "Monitoring Agent: Tracking insurance verification status",
            "next_field": "monitor_insurance_message"
        }

    try:
        patient_name = insurance_data['patient_name']
        notification_type = "INSURANCE_VERIFIED" if insurance_data.get("insurance_found") else "INSURANCE_NOT_FOUND"
        
        if insurance_data.get("insurance_found"):
            notification_result = await notify_insurance_status(
                session_data=session_data,
                patient_name=patient_name,
                insurance_data=insurance_data,
                message_type=notification_type
            )
            if isinstance(notification_result, dict) and notification_result.get("status") == "show_message":
                return notification_result
        else:
            notification_result = await notify_insurance_status(
                session_data=session_data,
                patient_name=patient_name,
                insurance_data=insurance_data,
                message_type=notification_type
            )
            if isinstance(notification_result, dict) and notification_result.get("status") == "show_message":
                return notification_result

        print(f"Notification Status: {notification_result.get('status', 'unknown')}")
        if notification_result.get("status") == "failure":
            print(f"Email Error: {notification_result.get('message')}")

    except Exception as e:
        print(f"Insurance monitoring failed: {str(e)}")
        return {"status": "error", "message": f"Insurance monitoring failed: {str(e)}"}

def format_clinical_summary(clinical_data: dict) -> dict:
    return {
        "diagnosis": clinical_data.get("diagnosis", "Pending diagnosis"),
        "treatment_plan": "\n- ".join(clinical_data.get("treatment_plan", ["No treatment plan"])),
        "diagnostic_tests": ", ".join(clinical_data.get("diagnostic_test", ["No tests required"])),
        "follow_up_date": clinical_data.get("follow_up", "No follow-up scheduled"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

async def handle_new_appointment(details: dict) -> str:
    return (
        "New appointment confirmed:\n"
        f"Date: {details.get('start', 'N/A')}\n"
    )

async def handle_reschedule(current_details: dict, original_details: dict) -> str:
    return (
        "Appointment rescheduled:\n"
        f"Original: {original_details.get('start', 'N/A')}\n"
        f"New Time: {current_details.get('start', 'N/A')}\n"
        f"Changes: {find_changes(original_details, current_details)}"
    )

async def handle_deletion(previous_details: dict) -> str:
    return (
        "Appointment cancelled:\n"
        f"Original Date: {previous_details.get('start', 'N/A')}\n"
    )

def find_changes(old: dict, new: dict) -> str:
    changes = []
    for key in ['start']:
        old_val = old.get(key, 'N/A')
        new_val = new.get(key, 'N/A')
        if old_val != new_val:
            changes.append(f"{key}: {old_val} → {new_val}")
    return "\n".join(changes) if changes else "No significant changes"

monitoring_agent = AssistantAgent(
    name="MonitoringAgent",
    model_client=model_client,
    system_message="You are Monitoring Agent. Watch for appointment, patient-case, and insurance status changes; format succinct update summaries; and trigger notifications.",
    tools=[monitor_appointments, monitor_patient_case, monitor_insurance_verification],
    reflect_on_tool_use=True
)