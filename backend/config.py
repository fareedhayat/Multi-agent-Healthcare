from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
# from appointment import appointment_agent
# from doctor import doctor_agent
# from clinical_recommendation import clinical_recommendation_agent
# from insurance_verfication import insurance_verification_agent
# from patient_intake import patient_intake_agent
# from monitoring import monitoring_agent
# from notification import notification_agent
from dotenv import load_dotenv
import os 

load_dotenv()

model_client = AzureOpenAIChatCompletionClient(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    model=os.getenv("AZURE_OPENAI_MODEL_NAME"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
)

# agents = [appointment_agent, doctor_agent, insurance_verification_agent, monitoring_agent, notification_agent, patient_intake_agent, clinical_recommendation_agent]

# model_client = AzureOpenAIChatCompletionClient(
#     azure_deployment="gpt-4o",
#     endpoint="https://multi-agent-oai.openai.azure.com/",
#     model="gpt-4o",
#     api_key="BYFJLSJ2DyFXnOCnFZrES9ZR92nZ5hSHBFDJYj7YOf9DKPsVsQJ8JQQJ99BEACYeBjFXJ3w3AAABACOGLyWq",
#     api_version="2024-12-01-preview",
# )

# model_client = AzureOpenAIChatCompletionClient(
#     azure_deployment="gpt-4o",
#     endpoint="https://macae-openai-s2vl7wsucnwym.openai.azure.com/",
#     model="gpt-4o",
#     api_key="3881615e7ef9404f96d0247dab7dbb9a",
#     api_version="2024-08-01-preview",
# )
