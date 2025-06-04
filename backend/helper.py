import os
from dotenv import load_dotenv
from msgraph import GraphServiceClient
from azure.identity import ClientSecretCredential
from msgraph.generated.models.event import Event
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.date_time_time_zone import DateTimeTimeZone
from msgraph.generated.models.location import Location
from msgraph.generated.models.attendee import Attendee
from msgraph.generated.models.email_address import EmailAddress
from msgraph.generated.models.attendee_type import AttendeeType
from msgraph.generated.users.item.events.item.event_item_request_builder import EventItemRequestBuilder
from msgraph.generated.users.item.calendar.calendar_view.calendar_view_request_builder import CalendarViewRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from general_question import GENERAL_QUESTIONS
from datetime import datetime, time, timedelta
from dateutil import parser
from typing import List, Dict, Any
import re
import uuid
import asyncio
import pytz
from pprint import pprint

load_dotenv()

tenant_id = os.getenv("TENANT_ID")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
doctor_email = 'aliciat@CRM422952.onmicrosoft.com'

credential = ClientSecretCredential(
    tenant_id=tenant_id,
    client_id=client_id,
    client_secret=client_secret
)

graph_client = GraphServiceClient(
    credentials=credential,
    scopes=["https://graph.microsoft.com/.default"]
)

async def create_outlook_event(
    patient_name: str,
    start_datetime: str,
    end_datetime: str,
) -> dict:
    event = Event(
        subject=f'Appointment with {patient_name}',
        start=DateTimeTimeZone(
            date_time=start_datetime,
            time_zone='Asia/Karachi',
        ),
        end=DateTimeTimeZone(
            date_time=end_datetime,
            time_zone='Asia/Karachi',
        ),
        location=Location(
            display_name="Hospital",
        ),
        attendees=[ Attendee(
			email_address = EmailAddress(
				address = doctor_email,
				name = "Adele Vance",
			),
			type = AttendeeType.Required,
		),
	],
        transaction_id=str(uuid.uuid4())
    )

    response = await graph_client.users.by_user_id(doctor_email).events.post(event)
    appointment_id = getattr(response, "id", None)
    print(appointment_id)
    return response

async def delete_outlook_event(appointment_id: str) -> str:
    response = await graph_client.users.by_user_id(doctor_email).events.by_event_id(appointment_id).delete()
    if response == None:
        return True
    else:
        return False

async def get_event_details(appointment_id: str) -> str:
    print("get_event_details.")
    query_params = EventItemRequestBuilder.EventItemRequestBuilderGetQueryParameters(
		select = ["subject", "start"],
    )

    request_configuration = RequestConfiguration(
    query_parameters = query_params,
    )

    result = await graph_client.users.by_user_id(doctor_email).events.by_event_id(appointment_id).get(request_configuration = request_configuration)
    
    details = await parse_event_details(result)
    return details

async def parse_event_details(result):
    # print(result)
    subject = result.subject
    
    match = re.search(r'Appointment with (.+)', subject, re.IGNORECASE)
    if match:
        # print(match.group(1).strip())
        patient_name = match.group(1).strip()

    start_time = result.start.date_time
    start_time_pkt = convert_utc_to_pkt(start_time)

    return {
        'subject': subject,
        'patient_name': patient_name,
        'start': start_time_pkt
    }

def convert_utc_to_pkt(utc_time_str: str) -> str:
    clean_time = utc_time_str.split('.')[0]  # remove subsecond precision
    dt_utc = datetime.fromisoformat(clean_time).replace(tzinfo=pytz.UTC)
    dt_pkt = dt_utc.astimezone(pytz.timezone("Asia/Karachi"))
    return dt_pkt.strftime("%Y-%m-%d %H:%M:%S %Z%z")

async def get_events(date: str):
    selected_date = datetime.strptime(date, "%Y-%m-%d").date()
    timezone = pytz.timezone("Asia/Karachi")

    start_datetime = timezone.localize(datetime.combine(selected_date, time(18, 0)))
    end_datetime = timezone.localize(datetime.combine(selected_date, time(22, 0)))

    query_params = CalendarViewRequestBuilder.CalendarViewRequestBuilderGetQueryParameters(
		start_date_time=start_datetime.isoformat(),
        end_date_time=end_datetime.isoformat(),
    )

    request_configuration = RequestConfiguration(
    query_parameters = query_params,
    )

    result = await graph_client.users.by_user_id("aliciat@CRM422952.onmicrosoft.com").calendar.calendar_view.get(request_configuration = request_configuration)
    busy_slots = []
    for event in result.value:
        start = datetime.fromisoformat(event.start.date_time)
        end = datetime.fromisoformat(event.end.date_time)

        start_local = start.replace(tzinfo=pytz.UTC).astimezone(timezone)
        end_local   = end.replace(tzinfo=pytz.UTC).astimezone(timezone)

        busy_slots.append({
            "start": start_local,
            "end": end_local
        })

    return (busy_slots)


def get_free_slots(date: str, busy_slots: list[str]) -> list[str]:
    all_slots = []
    timezone = pytz.timezone("Asia/Karachi")
    date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    start = timezone.localize(datetime.combine(date_obj, time(18, 0)))
    end = timezone.localize(datetime.combine(date_obj, time(22, 0)))


    slot_duration = timedelta(minutes=30)
    free_slots = []
    
    current = start
    while current < end:
        slot_end = current + slot_duration
        conflict = False

        for busy in busy_slots:
            busy_start = busy["start"]
            busy_end = busy["end"]

            if (current < busy_end) and (slot_end > busy_start):
                conflict = True
                break
                
        if not conflict:
            free_slots.append(current.strftime("%H:%M"))
        
        current += slot_duration
    
    return free_slots

def normalize_date(date_input: str) -> str:
    """
    Parse anything like 'today', '2025-4-12', '2025-04-12' 
    and return a strict ISO date 'YYYY-MM-DD'.
    """
    d = date_input.strip().lower()
    if d == "today":
        return datetime.now().date().isoformat()
    if d == "tomorrow":
        return (datetime.now().date() + timedelta(days=1)).isoformat()
    # flexibly parse any valid date string
    parsed = parser.parse(d)
    return parsed.date().isoformat() 

def normalize_time(time_input: str) -> str:
    """
    Parse '9', '9 PM', '09:00' etc. and return 'HH:MM'.
    """
    dt = parser.parse(time_input.strip())
    return dt.strftime("%H:%M")


# asyncio.run((get_events('2025-04-29')))