from autogen_agentchat.agents import AssistantAgent
from config import model_client 
from appointment import schedule_appointment, reschedule_appointment, delete_appointment
from clinical_recommendation import generate_clinical_recommendations, generate_medical_kb
from doctor import review_patient_case
from insurance_verfication import verify_patient_coverage, get_insurance_id
from monitoring import monitor_appointments, monitor_patient_case, monitor_insurance_verification
from notification import notify_appointment, notify_clinical_review, notify_insurance_status, send_email
from patient_intake import collect_basic_info, get_current_situation, collect_medical_history

appointment_agent = AssistantAgent(
    name="AppointmentAgent",
    model_client=model_client,
    system_message="",
    handoffs=["executor"],
    tools=[schedule_appointment, reschedule_appointment, delete_appointment]
)

clinical_recommendation_agent = AssistantAgent(
    name="ClinicalRecommendationAgent",
    model_client=model_client,
    system_message="",
    handoffs=["executor"],
    tools=[generate_medical_kb, generate_clinical_recommendations]
)

doctor_agent = AssistantAgent(
    name="DoctorAgent",
    model_client=model_client,
    system_message="",
    handoffs=["executor"],
    tools=[review_patient_case],
)

insurance_verification_agent = AssistantAgent(
    name="InsuranceVerificationAgent",
    model_client=model_client,
    system_message="",
    handoffs=["executor"],
    tools=[verify_patient_coverage, get_insurance_id],
)

monitoring_agent = AssistantAgent(
    name="MonitoringAgent",
    model_client=model_client,
    system_message="",
    handoffs=["executor"],
    tools=[monitor_appointments, monitor_patient_case, monitor_insurance_verification],
)

notification_agent = AssistantAgent(
    name="NotificationAgent",
    model_client=model_client,
    system_message="",
    handoffs=["executor"],
    tools=[notify_appointment, notify_clinical_review, notify_insurance_status, send_email],
)

patient_intake_agent = AssistantAgent(
    name="PatientIntakeAgent",
    model_client=model_client,
    system_message="",
    handoffs=["executor"],
    tools=[collect_basic_info, get_current_situation, collect_medical_history],
)
