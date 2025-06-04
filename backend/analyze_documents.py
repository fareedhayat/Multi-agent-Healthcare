import os
from typing import List, Dict, Any
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient, DocumentLine, AnalyzeResult
import asyncio
import re
from dotenv import load_dotenv

load_dotenv()

endpoint = os.getenv("AZURE_ENDPOINT")
key = os.getenv("AZURE_KEY")

document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)
# "prebuilt-layout"

async def analyze_previous_records(file_path: str) -> Dict[str, list[str]]:
    with open(file_path, "rb") as file:
        poller = document_analysis_client.begin_analyze_document("prebuilt-document", document=file)
    
    result = poller.result() 
    # print(result)

    patient_info = extract_patient_info(result.key_value_pairs)
    # print(patient_info)

    medication_info = extract_medications_info(result)
    # print(medication_info)

    return patient_info, medication_info

def extract_medications_info(result: AnalyzeResult) -> List[Dict[str, str]]:
    """Extracts medication table lines from the first page of the result."""
    all_lines = [line.content for page in result.pages for line in page.lines]
    try:
        idx = next(i for i, t in enumerate(all_lines) if t.strip().lower() == "drugs")
    except StopIteration:
        return []

    data_start = idx + 3

    med_lines = []
    for line in all_lines[data_start:]:
        text = line.strip()
        if not text:
            break
        if re.match(r"^[A-Za-z ]+:$", text):
            break
        med_lines.append(text)

    return extract_medication_info(med_lines)

def extract_medication_info(lines: List[str]) -> List[Dict[str, str]]:
    meds = []
    buffer = []
    for text in lines:
        t = text.strip()
        if re.match(r"^[A-Za-z ]+:", t):
            break
        if not t or re.match(r"^\d+\.$", t):
            continue
        buffer.append(t)
        if len(buffer) == 3:
            name, unit, dosage = buffer
            meds.append({"name": name, "unit": unit, "dosage": dosage})
            buffer.clear()
    return meds

def extract_patient_info(kvps: List[Dict[str, Any]]) -> Dict[str, Any]:
    result = {
        "patient_name": "Unknown Patient",  # Default value
        "date": None,
        "dob": None,
        "age": None,
        "sex": None,
        "address": None,
        "blood_pressue": None,
        "pulse_rate": None,
        "weight": None,
        "allergies": None
    }
    # print(kvps)
    for kv in kvps:
        key = kv.key.content
        k = norm(key)
        val = kv.value.content.strip() if kv.value and kv.value.content else ""
        if not val:
            continue

        if "patient's name" in k:
            result["patient_name"] = val
        elif k == "date":
            result["date"] = val
        elif "date of birth" in k or k == "dob":
            result["dob"] = val
        elif k == "age":
            result["age"] = val
        elif k == "sex":
            result["sex"] = val
        elif "patient's address" in k or "address" == k:
            result["address"] = val
        elif "blood pressure":
            result["blood_pressue"] = val
        elif "pulse rate":
            result["pulse_rate"] = val
        elif "weight":
            result["weight"] = val
        elif "allergies":
            result["allergies"] = val

    return result

def norm(key: str) -> str:
    return key.strip().lower().rstrip(":")


# asyncio.run(analyze_previous_records("Prescription 1.jpg"))