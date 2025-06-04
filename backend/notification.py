# '''
# Send notifications
# '''
# from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
# from config import model_client
# import requests
# from access_token import get_access_token
# from datetime import datetime
# from dateutil import parser, tz
# import platform
# from typing import List, Any 
# from tool_decorator import label_tool 

# PATIENT_TEMPLATES = {
#     "created": """
#     <h3>Appointment Confirmed</h3>
#     <p>Dear {patient_name},</p>
#     <p>Your appointment has been scheduled for:</p>
#     <p><strong>{date}</strong> at <strong>{time}</strong></p>
#     {signature}
#     """,
    
#     "rescheduled": """
#     <h3>Appointment Updated</h3>
#     <p>Dear {patient_name},</p>
#     <p>Your appointment has been rescheduled to:</p>
#     <p><strong>{date}</strong> at <strong>{time}</strong></p>
#     {signature}
#     """,
    
#     "deleted": """
#     <h3>Appointment Cancelled</h3>
#     <p>Dear {patient_name},</p>
#     <p>Your appointment has been cancelled.</p>
#     {signature}
#     """
# }

# DOCTOR_TEMPLATES = {
#     "created": """
#     <h3>New Appointment Scheduled</h3>
#     <p>New patient appointment:</p>
#     <ul>
#         <li>Patient: {patient_name}</li>
#         <li>Date: {date}</li>
#         <li>Time: {time}</li>
#     </ul>
#     {signature}
#     """,
    
#     "rescheduled": """
#     <h3>Appointment Rescheduled</h3>
#     <p>Appointment update for {patient_name}:</p>
#     <p>New time: {date} at {time}</p>
#     {signature}
#     """,
    
#     "deleted": """
#     <h3>Appointment Cancelled</h3>
#     <p>Appointment with {patient_name} has been cancelled.</p>
#     {signature}
#     """
# }

# PATIENT_CASE_REVIEW_TEMPLATE = """
#     <h3>Medical Review Summary for {patient_name}</h3>
#     <p><strong>Date:</strong> {timestamp}</p>
    
#     <div style="margin: 20px 0;">
#         <h4>Diagnosis:</h4>
#         <p>{diagnosis}</p>
        
#         <h4>Recommended Treatment Plan:</h4>
#         <ul>
#             {treatment_plan}
#         </ul>
        
#         <h4>Required Tests:</h4>
#         <p>{diagnostic_tests}</p>
        
#         <h4>Follow-Up Date:</h4>
#         <p>{follow_up_date}</p>
#     </div>
    
#     <p style="color: #666;">
#         {signature}
#     </p>
# """

# INSURANCE_FOUND_TEMPLATE = """
#     <h3>Insurance Verification Complete</h3>
#     <p><strong>Patient:</strong> {patient_name}</p>
#     <p><strong>Service:</strong> {service}</p>
#     <p><strong>Date:</strong> {timestamp}</p>
    
#     <div style="margin: 20px 0;">
#         {status_message}
#         {coverage_details}
#     </div>
    
#     <p style="color: #666;">
#         {signature}
#     </p>
# """

# COVERAGE_STATUS_BLOCK = """
#         {status_icon} {status_message}
#         <ul>
#             {coverage_details}
#         </ul>
# """

# COVERAGE_DETAILS = """
#             <li>Provider: {provider}</li>
#             <li>Copay Amount: {copay}</li>
#             <li>Authorization Required: {authorization_required}</li>
# """

# NOT_COVERED_MESSAGE = """
#         <h4 style="color: #cc0000;">✗ This service is not covered</h4>
#         <p>Service "{service}" is not included in your insurance plan.</p>
# """

# INSURANCE_NOT_FOUND_TEMPLATE = """
# <html>
# <body>
#     <h3>Insurance Verification Issue</h3>
#     <p><strong>Patient:</strong> {patient_name}</p>
#     <p><strong>Date:</strong> {timestamp}</p>
    
#     <div style="margin: 20px 0; color: #cc0000;">
#         <h4>Verification Failed:</h4>
#         <p>{error_message}</p>
#     </div>
    
#     <p style="color: #666;">
#         Please contact our support team for assistance.<br>
#         {signature}
#     </p>
# </body>
# </html>
# """

# signature = (
#     "<strong>HealthCare Agent</strong><br>"
#     "OZ Digital Consulting<br>"
# )

# token_response = get_access_token()
# access_token = token_response["data"]

# user_email = 'annew@CRM422952.onmicrosoft.com'
# doctor_email = 'aliciat@CRM422952.onmicrosoft.com'

# async def send_email(email_subject: str, token: str, blob_name: str, recipient_emails: List[str], **kwargs: Any):
#     try:
#         url = f'https://graph.microsoft.com/v1.0/users/{doctor_email}/sendMail'
#         headers = {
#             "Authorization": f"Bearer {token}",
#         }
#         email_template = blob_name

#         email_content = email_template.format(
#             **kwargs,
#         )

#         email_msg = {'Message':
#                         {'Subject': email_subject,
#                                 'Body': {
#                                     'ContentType': 'HTML',
#                                     'Content': email_content
#                                 },
#                             'ToRecipients':[{"EmailAddress": {"Address": email}} for email in recipient_emails],
#                         },
#                             'SaveToSentItems': 'true'
#                     }
        
#         email = requests.post(url, headers=headers, json=email_msg)

#         if email.status_code == 202:
#             return {"status": "success", 
#                     "message": "Email sent successfully."}
#         else:
#             return {"status": "failure", 
#                     "message": f"Failed to send email. {email.status_code}"}

#     except Exception as e:
#         return {"status": "exception", 
#                 "message": f"An exception occured while sending notification.",
#                 "exception_message": str(e)}

# def format_patient_message(details: dict, messages: list) -> str:
    
#     date_str, time_str = format_time(details.get('start', ''))
    
#     return {
#         'patient_name': details.get('patient_name', 'Patient'),
#         'date': date_str,
#         'time': time_str,
#         'signature': signature
#     }

# def format_doctor_message(details: dict, messages: list) -> str:
    
#     date_str, time_str = format_time(details.get('start', ''))
    
#     return {
#         'patient_name': details.get('patient_name', 'Patient'),
#         'date': date_str,
#         'time': time_str,
#         'signature': signature
#     }

# def format_time(datetime_str: str) -> tuple:
#     """Convert custom datetime string to formatted PKT time"""
#     try:

#         dt_str = datetime_str.replace(' PKT+', '+').replace(' ', 'T')
#         dt = parser.parse(dt_str)

#         pkt = tz.gettz('Asia/Karachi')

#         if dt.tzinfo is None:
#             dt = dt.replace(tzinfo=pkt)
#         else:
#             dt = dt.astimezone(pkt)

#         if platform.system() == 'Windows':
#             time_fmt = "%#I:%M %p"
#         else:
#             time_fmt = "%-I:%M %p"
        
#         date_str = dt.strftime("%B %d, %Y")
#         time_str = dt.strftime(time_fmt) + " PKT"
        
#         return date_str, time_str
        
#     except Exception as e:
#         print(f"Time parsing error: {str(e)}")
#         return ("Unknown date", "Unknown time")

# def format_insurance_parameters(data: dict) -> dict:
#     """Ensure all template parameters are present"""
#     base_params = {
#         "patient_name": data.get("patient_name", "Patient"),
#         "service": data.get("service", "Unknown Service"),
#         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
#         "signature": signature,
#         "status_message": "",
#         "coverage_details": ""
#     }
    
#     if data.get("insurance_found"):
#         coverage_status = "covered" if data.get("service_covered") else "not covered"
#         base_params["status_message"] = f'Service {coverage_status}'
        
#         if data.get("service_covered"):
#             base_params["coverage_details"] = """
#                 <ul>
#                     <li>Provider: {provider}</li>
#                     <li>Copay Amount: {copay}</li>
#                     <li>Authorization Required: {auth_required}</li>
#                 </ul>
#             """.format(
#                 provider=data.get("provider", "Unknown"),
#                 copay=f"${data.get('coverage_details', {}).get('copay', 0)}",
#                 auth_required="Yes" if data.get('coverage_details', {}).get('requires_authorization') else "No"
#             )
#         else:
#             base_params["coverage_details"] = f'<p>Service "{data.get("service")}" is not covered under this plan.</p>'
    
#     return base_params

# @label_tool("Notifying the doctor and patient about appointment.")
# async def notify_appointment(current_details: dict, messages: list, session_data: dict = None):
#     if session_data is None:
#         session_data = {}

#     template_type = "created" if "confirmed" in messages[0] else "rescheduled" if "rescheduled" in messages[0] else "deleted" if "cancelled" in messages[0] else 'nothing'
    
#     patient_template = PATIENT_TEMPLATES[template_type]
#     doctor_template = DOCTOR_TEMPLATES[template_type]

#     patient_params = format_patient_message(current_details, messages)
#     doctor_params = format_doctor_message(current_details, messages)
    
#     patient_noti_status = await send_email(
#         email_subject=f"Your Appointment: {current_details['subject']}",
#         token=access_token,
#         blob_name=patient_template,
#         recipient_emails=[user_email],
#         **patient_params
#     )

#     doctor_noti_status = await send_email(
#         email_subject=f"Appointment Update: {current_details['patient_name']}",
#         token=access_token,
#         blob_name=doctor_template,
#         recipient_emails=[doctor_email],
#         **doctor_params
#     )

#     if patient_noti_status['status'] == "success" and doctor_noti_status['status'] == "success": 
#         if "monitor_appointment_message" not in session_data:
#             return {
#                 "status": "show_message",
#                 "message": "Notification Agent: Sending the details of appointment via email.",
#                 "next_field": "monitor_appointment_message"
#             }
        
#     print(f"Patient Status: {patient_noti_status}")
#     print(f"Doctor Status: {doctor_noti_status}") 

# async def notify_clinical_review(patient_name: str, message_params: dict, session_data: dict = None):
#     if session_data is None:
#         session_data = {}
    
#     print('notify clinical review function')
#     print(patient_name) 

#     params = {
#             "signature": signature,
#             "patient_name": patient_name
#         }
#     params.update(message_params)
#     clinical_review_noti_status = await send_email(
#         email_subject=f"Medical Review Summary",
#         token=access_token,
#         blob_name=PATIENT_CASE_REVIEW_TEMPLATE,
#         recipient_emails=[user_email],
#         **params
#     )

#     if clinical_review_noti_status["status"] == "success": 
#         if "notify_clinical_review_message" not in session_data:
#             return {
#                 "status": "show_message",
#                 "message": "Notification Agent: Sending a notification via email of the review report.",
#                 "next_field": "notify_clinical_review_message"
#             }

#     return (f"Clinical Review Status: {clinical_review_noti_status}") 

# async def notify_insurance_status(patient_name: str, insurance_data: dict, message_type: str, session_data: dict = None):
#     if session_data is None:
#         session_data = {}
    
#     """Works with existing send_email function"""
#     try:
#         params = format_insurance_parameters(insurance_data)
        
#         return await send_email(
#             email_subject=f"Insurance Update - {patient_name}",
#             token=access_token,
#             blob_name=INSURANCE_FOUND_TEMPLATE,
#             recipient_emails=[user_email],
#             **params
#         )
        
#     except Exception as e:
#         print(f"Insurance notification failed: {str(e)}")
#         return {"status": "error", "message": str(e)}
    
# notification_agent = AssistantAgent(
#     name="NotificationAgent",
#     model_client=model_client,
#     system_message="You are Notification Agent. Prepare and send templated HTML emails via Graph API for appointments, clinical reviews, and insurance updates. Log and report send status.",
#     tools=[notify_appointment, notify_clinical_review, notify_insurance_status, send_email],
#     reflect_on_tool_use=True
# ) 




'''
Send notifications
'''
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from config import model_client
import requests
from access_token import get_access_token
from datetime import datetime
from dateutil import parser, tz
import platform
from typing import List, Any
from tool_decorator import label_tool

PATIENT_TEMPLATES = {
    "created": """
    <h3>Appointment Confirmed</h3>
    <p>Dear {patient_name},</p>
    <p>Your appointment has been scheduled for:</p>
    <p><strong>{date}</strong> at <strong>{time}</strong></p>
    {signature}
    """,
    
    "rescheduled": """
    <h3>Appointment Updated</h3>
    <p>Dear {patient_name},</p>
    <p>Your appointment has been rescheduled to:</p>
    <p><strong>{date}</strong> at <strong>{time}</strong></p>
    {signature}
    """,
    
    "deleted": """
    <h3>Appointment Cancelled</h3>
    <p>Dear {patient_name},</p>
    <p>Your appointment has been cancelled.</p>
    {signature}
    """
}

DOCTOR_TEMPLATES = {
    "created": """
    <h3>New Appointment Scheduled</h3>
    <p>New patient appointment:</p>
    <ul>
        <li>Patient: {patient_name}</li>
        <li>Date: {date}</li>
        <li>Time: {time}</li>
    </ul>
    {signature}
    """,
    
    "rescheduled": """
    <h3>Appointment Rescheduled</h3>
    <p>Appointment update for {patient_name}:</p>
    <p>New time: {date} at {time}</p>
    {signature}
    """,
    
    "deleted": """
    <h3>Appointment Cancelled</h3>
    <p>Appointment with {patient_name} has been cancelled.</p>
    {signature}
    """
}

PATIENT_CASE_REVIEW_TEMPLATE = """
    <h3>Medical Review Summary for {patient_name}</h3>
    <p><strong>Date:</strong> {timestamp}</p>
    
    <div style="margin: 20px 0;">
        <h4>Diagnosis:</h4>
        <p>{diagnosis}</p>
        
        <h4>Recommended Treatment Plan:</h4>
        <ul>
            {treatment_plan}
        </ul>
        
        <h4>Required Tests:</h4>
        <p>{diagnostic_tests}</p>
        
        <h4>Follow-Up Date:</h4>
        <p>{follow_up_date}</p>
    </div>
    
    <p style="color: #666;">
        {signature}
    </p>
"""

INSURANCE_FOUND_TEMPLATE = """
    <h3>Insurance Verification Complete</h3>
    <p><strong>Patient:</strong> {patient_name}</p>
    <p><strong>Service:</strong> {service}</p>
    <p><strong>Date:</strong> {timestamp}</p>
    
    <div style="margin: 20px 0;">
        {status_message}
        {coverage_details}
    </div>
    
    <p style="color: #666;">
        {signature}
    </p>
"""

COVERAGE_STATUS_BLOCK = """
        {status_icon} {status_message}
        <ul>
            {coverage_details}
        </ul>
"""

COVERAGE_DETAILS = """
            <li>Provider: {provider}</li>
            <li>Copay Amount: {copay}</li>
            <li>Authorization Required: {authorization_required}</li>
"""

NOT_COVERED_MESSAGE = """
        <h4 style="color: #cc0000;">✗ This service is not covered</h4>
        <p>Service "{service}" is not included in your insurance plan.</p>
"""

INSURANCE_NOT_FOUND_TEMPLATE = """
<html>
<body>
    <h3>Insurance Verification Issue</h3>
    <p><strong>Patient:</strong> {patient_name}</p>
    <p><strong>Date:</strong> {timestamp}</p>
    
    <div style="margin: 20px 0; color: #cc0000;">
        <h4>Verification Failed:</h4>
        <p>{error_message}</p>
    </div>
    
    <p style="color: #666;">
        Please contact our support team for assistance.<br>
        {signature}
    </p>
</body>
</html>
"""

signature = (
    "<strong>HealthCare Agent</strong><br>"
    "OZ Digital Consulting<br>"
)

token_response = get_access_token()
access_token = token_response["data"]

user_email = 'annew@CRM422952.onmicrosoft.com'
doctor_email = 'aliciat@CRM422952.onmicrosoft.com'

async def send_email(email_subject: str, token: str, blob_name: str, recipient_emails: List[str], **kwargs: Any):
    try:
        url = f'https://graph.microsoft.com/v1.0/users/{doctor_email}/sendMail'
        headers = {
            "Authorization": f"Bearer {token}",
        }
        email_template = blob_name

        email_content = email_template.format(
            **kwargs,
        )

        email_msg = {'Message':
                        {'Subject': email_subject,
                                'Body': {
                                    'ContentType': 'HTML',
                                    'Content': email_content
                                },
                            'ToRecipients':[{"EmailAddress": {"Address": email}} for email in recipient_emails],
                        },
                            'SaveToSentItems': 'true'
                    }
        
        email = requests.post(url, headers=headers, json=email_msg)

        if email.status_code == 202:
            return {"status": "success", 
                    "message": "Email sent successfully."}
        else:
            return {"status": "failure", 
                    "message": f"Failed to send email. {email.status_code}"}

    except Exception as e:
        return {"status": "exception", 
                "message": f"An exception occured while sending notification.",
                "exception_message": str(e)}

def format_patient_message(details: dict, messages: list) -> str:
    
    date_str, time_str = format_time(details.get('start', ''))
    
    return {
        'patient_name': details.get('patient_name', 'Patient'),
        'date': date_str,
        'time': time_str,
        'signature': signature
    }

def format_doctor_message(details: dict, messages: list) -> str:
    
    date_str, time_str = format_time(details.get('start', ''))
    
    return {
        'patient_name': details.get('patient_name', 'Patient'),
        'date': date_str,
        'time': time_str,
        'signature': signature
    }

def format_time(datetime_str: str) -> tuple:
    """Convert custom datetime string to formatted PKT time"""
    try:

        dt_str = datetime_str.replace(' PKT+', '+').replace(' ', 'T')
        dt = parser.parse(dt_str)

        pkt = tz.gettz('Asia/Karachi')

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=pkt)
        else:
            dt = dt.astimezone(pkt)

        if platform.system() == 'Windows':
            time_fmt = "%#I:%M %p"
        else:
            time_fmt = "%-I:%M %p"
        
        date_str = dt.strftime("%B %d, %Y")
        time_str = dt.strftime(time_fmt) + " PKT"
        
        return date_str, time_str
        
    except Exception as e:
        print(f"Time parsing error: {str(e)}")
        return ("Unknown date", "Unknown time")

def format_insurance_parameters(data: dict) -> dict:
    """Ensure all template parameters are present"""
    base_params = {
        "patient_name": data.get("patient_name", "Patient"),
        "service": data.get("service", "Unknown Service"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "signature": signature,
        "status_message": "",
        "coverage_details": ""
    }
    
    if data.get("insurance_found"):
        coverage_status = "covered" if data.get("service_covered") else "not covered"
        base_params["status_message"] = f'Service {coverage_status}'
        
        if data.get("service_covered"):
            base_params["coverage_details"] = """
                <ul>
                    <li>Provider: {provider}</li>
                    <li>Copay Amount: {copay}</li>
                    <li>Authorization Required: {auth_required}</li>
                </ul>
            """.format(
                provider=data.get("provider", "Unknown"),
                copay=f"${data.get('coverage_details', {}).get('copay', 0)}",
                auth_required="Yes" if data.get('coverage_details', {}).get('requires_authorization') else "No"
            )
        else:
            base_params["coverage_details"] = f'<p>Service "{data.get("service")}" is not covered under this plan.</p>'
    
    return base_params

@label_tool("Notifying the doctor and patient about appointment.")
async def notify_appointment(session_data: dict = None, current_details: dict = None, messages: list = None):
    if session_data is None:
        session_data = {}

    if "notify_appointment_message" not in session_data:
        return {
            "status": "show_message",
            "message": "Notification Agent: Sending appointment notifications to doctor and patient",
            "next_field": "notify_appointment_message"
        }

    # print(current_details)
    template_type = "created" if "confirmed" in messages[0] else "rescheduled" if "rescheduled" in messages[0] else "deleted" if "cancelled" in messages[0] else 'nothing'
    
    patient_template = PATIENT_TEMPLATES[template_type]
    doctor_template = DOCTOR_TEMPLATES[template_type]

    patient_params = format_patient_message(current_details, messages)
    doctor_params = format_doctor_message(current_details, messages)
    
    patient_noti_status = await send_email(
        email_subject=f"Your Appointment: {current_details['subject']}",
        token=access_token,
        blob_name=patient_template,
        recipient_emails=[user_email],
        **patient_params
    )

    doctor_noti_status = await send_email(
        email_subject=f"Appointment Update: {current_details['patient_name']}",
        token=access_token,
        blob_name=doctor_template,
        recipient_emails=[doctor_email],
        **doctor_params
    )

    print(f"Patient Status: {patient_noti_status}")
    print(f"Doctor Status: {doctor_noti_status}") 

async def notify_clinical_review(session_data: dict = None, patient_name: str = None, message_params: dict = None):
    if session_data is None:
        session_data = {}

    if "notify_clinical_message" not in session_data:
        return {
            "status": "show_message",
            "message": "Notification Agent: Sending clinical review summary to patient",
            "next_field": "notify_clinical_message"
        }

    print('notify clinical review function')
    print(patient_name)
    params = {
            "signature": signature,
            "patient_name": patient_name
        }
    params.update(message_params)
    clinical_review_noti_status = await send_email(
        email_subject=f"Medical Review Summary",
        token=access_token,
        blob_name=PATIENT_CASE_REVIEW_TEMPLATE,
        recipient_emails=[user_email],
        **params
    )

    return (f"Clinical Review Status: {clinical_review_noti_status}") 

async def notify_insurance_status(session_data: dict = None, patient_name: str = None, insurance_data: dict = None, message_type: str = None):
    if session_data is None:
        session_data = {}

    if "notify_insurance_message" not in session_data:
        return {
            "status": "show_message",
            "message": "Notification Agent: Sending insurance verification status to patient",
            "next_field": "notify_insurance_message"
        }

    """Works with existing send_email function"""
    try:
        params = format_insurance_parameters(insurance_data)
        
        return await send_email(
            email_subject=f"Insurance Update - {patient_name}",
            token=access_token,
            blob_name=INSURANCE_FOUND_TEMPLATE,
            recipient_emails=[user_email],
            **params
        )
        
    except Exception as e:
        print(f"Insurance notification failed: {str(e)}")
        return {"status": "error", "message": str(e)}
    
notification_agent = AssistantAgent(
    name="NotificationAgent",
    model_client=model_client,
    system_message="You are Notification Agent. Prepare and send templated HTML emails via Graph API for appointments, clinical reviews, and insurance updates. Log and report send status.",
    tools=[notify_appointment, notify_clinical_review, notify_insurance_status, send_email],
    reflect_on_tool_use=True
)