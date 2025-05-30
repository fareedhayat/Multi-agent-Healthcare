from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from helper import normalize_date, normalize_time, get_events, get_free_slots, create_outlook_event, delete_outlook_event, get_event_details
from monitoring import monitor_appointments 
from tool_decorator import label_tool
from datetime import datetime, time, timedelta
from dateutil import parser
from config import model_client
from utils import input_once 
import asyncio
'''
Coordinates between patient, doctors, and facilities
'''
@label_tool("Schedulling Appointment")
async def schedule_appointment(session_data: dict = None) -> str:
    if session_data is None:
        session_data = {}
    
    if "name" not in session_data:
        return {
            "status": "need_input",
            "prompt": "Please enter your name:",
            "next_field": "name"
        }
    
    # Check if we have all required information
    if "appointment_date" not in session_data:
        return {
            "status": "need_input",
            "prompt": "Enter appointment date (e.g. 2025-05-05 or May 5, 2025):",
            "next_field": "appointment_date"
        }
    
    if "appointment_time" not in session_data:
        date = normalize_date(session_data["appointment_date"])
        busy = await get_events(date)
        free_slots = get_free_slots(date, busy)
        
        if not free_slots:
            return {
                "status": "error",
                "message": f"Dr. is fully booked on {date}. Please choose another date."
            }
        
        # Store free slots in session data for validation
        session_data["free_slots"] = free_slots
        return {
            "status": "need_input",
            "prompt": f"Available slots on {date}:\n" + "\n".join(f"{i+1}. {slot}" for i, slot in enumerate(free_slots)) + "\n\nSelect a slot by number:",
            "next_field": "appointment_time",
            "free_slots": free_slots
        }
    
    # Validate slot selection
    if "free_slots" in session_data:
        try:
            choice = int(session_data["appointment_time"])
            if not (1 <= choice <= len(session_data["free_slots"])):
                return {
                    "status": "error",
                    "message": "Invalid selection. Please pick a valid number."
                }
            time = session_data["free_slots"][choice - 1]
            session_data["appointment_time"] = time
        except ValueError:
            return {
                "status": "error",
                "message": "Invalid selection. Please enter a number."
            }
    
    # We have all required information, proceed with scheduling
    date = normalize_date(session_data["appointment_date"])
    time = session_data["appointment_time"]
    patient_name = session_data.get("name", "Unknown Patient")
    
    start_iso = f"{date}T{time}:00"
    end_iso = (datetime.fromisoformat(start_iso) + timedelta(minutes=30)) \
        .strftime("%Y-%m-%dT%H:%M:%S")

    try:
        event = await create_outlook_event(
            patient_name=patient_name,
            start_datetime=start_iso,
            end_datetime=end_iso,
        )

        original_details = await get_event_details(event.id)
        await monitor_appointments(event.id, "created", original_details=original_details)

        return {
            "status": "complete",
            "message": (
                f"##### Appointment Scheduled \n"
                f"**Patient:** {patient_name}\n"
                f"**Date:** {date}\n"
                f"**Time:** {time}\n"
                f"**Appointment ID:** {event.id}\n\n"
                f"Your appointment has been added to the calendar."
            )
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to schedule appointment: {e}"
        }

async def reschedule_appointment(session_data: dict = None) -> str:
    if session_data is None:
        session_data = {}
    
    # Check if we have appointment ID
    if "appointment_id" not in session_data:
        return {
            "status": "need_input",
            "prompt": "Please enter the appointment ID:",
            "next_field": "appointment_id"
        }
    
    # Check if we have new date
    if "new_date" not in session_data:
        return {
            "status": "need_input",
            "prompt": "Please enter the new date (e.g. 2025-05-05 or May 5, 2025):",
            "next_field": "new_date"
        }
    
    # Get original appointment details
    original_details = await get_event_details(session_data["appointment_id"])
    patient_name = original_details.get('patient_name')
    
    if not patient_name:
        return {
            "status": "error",
            "message": f"Could not find details for appointment {session_data['appointment_id']}."
        }
    
    # Delete original appointment
    response = await delete_outlook_event(session_data["appointment_id"])
    if not response:
        return {
            "status": "error",
            "message": "Failed to reschedule appointment"
        }
    
    # Check if we have new time
    if "new_time" not in session_data:
        date = normalize_date(session_data["new_date"])
        busy = await get_events(date)
        free_slots = get_free_slots(date, busy)
        
        if not free_slots:
            return {
                "status": "error",
                "message": f"Dr. is fully booked on {date}. Please choose another date."
            }
        
        # Store free slots in session data for validation
        session_data["free_slots"] = free_slots
        return {
            "status": "need_input",
            "prompt": f"Available slots on {date}:\n" + "\n".join(f"{i+1}. {slot}" for i, slot in enumerate(free_slots)) + "\n\nSelect a slot by number:",
            "next_field": "new_time",
            "free_slots": free_slots
        }
    
    # Validate slot selection
    if "free_slots" in session_data:
        try:
            choice = int(session_data["new_time"])
            if not (1 <= choice <= len(session_data["free_slots"])):
                return {
                    "status": "error",
                    "message": "Invalid selection. Please pick a valid number."
                }
            time = session_data["free_slots"][choice - 1]
            session_data["new_time"] = time
        except ValueError:
            return {
                "status": "error",
                "message": "Invalid selection. Please enter a number."
            }
    
    # We have all required information, proceed with rescheduling
    date = normalize_date(session_data["new_date"])
    time = session_data["new_time"]
    
    start_iso = f"{date}T{time}:00"
    end_iso = (datetime.fromisoformat(start_iso) + timedelta(minutes=30)) \
        .strftime("%Y-%m-%dT%H:%M:%S")

    try:
        event = await create_outlook_event(
            patient_name=patient_name,
            start_datetime=start_iso,
            end_datetime=end_iso,
        )
        
        await monitor_appointments(event.id, "rescheduled", original_details=original_details)
        
        return {
            "status": "complete",
            "message": (
                f"##### Appointment Rescheduled\n"
                f"**Appointment ID:** {event.id}\n"
                f"**New Date:** {date}\n"
                f"**New Time:** {time}\n\n"
                f"Your appointment has been successfully rescheduled."
            )
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to schedule appointment: {e}"
        }

async def delete_appointment(session_data: dict = None) -> str:
    if session_data is None:
        session_data = {}
    
    # Check if we have appointment ID
    if "appointment_id" not in session_data:
        return {
            "status": "need_input",
            "prompt": "Please enter the appointment ID:",
            "next_field": "appointment_id"
        }

    current_details = await get_event_details(session_data["appointment_id"])
    response = await delete_outlook_event(session_data["appointment_id"])
    if not response:
        return (f"Failed to delete appointment")

    await monitor_appointments(session_data["appointment_id"], "deleted", current_details=current_details)
    return (
        f"##### Appointment Deleted\n"
        f"**Appointment ID:** {session_data['appointment_id']}\n"
        f"Your appointment has been successfully deleted."
    )

appointment_agent = AssistantAgent(
    name="AppointmentAgent",
    model_client=model_client,
    system_message="You are AppointmentAgent. Help users schedule, reschedule, or delete 30‑minute patient appointments via Outlook. Prompt for name and date, show available slots, call Graph API, and confirm success or errors in brief Markdown.",
    tools=[schedule_appointment, reschedule_appointment, delete_appointment]
)

# asyncio.run(schedule_appointment('haider ali', 'today'))
