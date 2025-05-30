import msal, os
from dotenv import load_dotenv
import logging
# from notifications import notify_exception

load_dotenv()

def get_access_token():
    try:
        tenantID = os.getenv("TENANT_ID")
        clientID = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")

        if not all([tenantID, clientID, client_secret]):
            return {
                "status": "failure",
                "message": "Missing required environment variables.",
                "data": None
            }

        authority = f'https://login.microsoftonline.com/{tenantID}'
        scope = ['https://graph.microsoft.com/.default']
        app = msal.ConfidentialClientApplication(clientID, authority=authority, client_credential=client_secret)
        access_token = app.acquire_token_for_client(scopes=scope) 

        if "access_token" not in access_token:
            return {
                "status": "failure",
                "message": "Failed to fetch access token.",
                "data": access_token.get("error_description")
            }

        return {
            "status": "success",
            "message": "Access token retrieved successfully.",
            "data": access_token["access_token"]
        }
    except Exception as e:
        logging.exception("An error occurred while fetching the access token.")
        return {
            "status": "failure",
            "message": f"An exception occurred: {str(e)}",
            "data": None
        }
