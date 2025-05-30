from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_core.models import SystemMessage
from dotenv import load_dotenv
from config import model_client
import os
from typing import List, Dict
import asyncio
import json
from pprint import pprint
import ast
from general_question import GENERAL_QUESTIONS

load_dotenv()

async def classify_user_input(user_input):
    prompt = f"""
    You are an AI healthcare assistant that first classifies the user's query into one of the following categories:

    - **greeting or general_conversation**: Basic user greetings (hello, hi, etc.) or a conversation 
    - **general_question**: Common medical questions that can be answered directly by an LLM and are related to GENERAL_QUESTIONS
    - **plan_required**: Anything that needs further processing or coordination via agents and functions

    Use the provided GENERAL_QUESTIONS and GREETINGS below to assist in classification.
    User Query:{user_input}
    GENERAL_QUESTIONS = {GENERAL_QUESTIONS}

    ---

    # Step 1: Classify the Query

    For the following user query, return ONLY the following formats:

    ### Case 1: Greeting

    {{
    "category": "greeting or general_conversation",
    "response": Response nicely and warmly and ask for anything else the user needs to ask
    }}

    ### Case 2: General Medical Question

    {{
    "category": "general_question",
    "response": "Your direct short answer here."
    }}

    ### Case 3: Requires Planning

    {{
    "category": "plan_required"
    }}
    """
    
    response = await model_client.create([SystemMessage(content=prompt)])

    plan_text = response.content.strip()

    return plan_text

# asyncio.run(classify_user_input("Hi, how are tou today"))

# Refactor process_user_input to handle interactive steps for API integration
async def process_user_input(user_input: str, session_data: dict = None) -> dict:
    if session_data is None:
        session_data = {}
    
    if user_input.lower() in {"exit", "quit"}:
        return {"response": "Goodbye!"}
    
    # If we're in the middle of collecting information
    if "current_step" in session_data:
        try:
            # Update the session data with the user's input
            current_field = session_data["current_step"]["next_field"]
            session_data[current_field] = user_input
            
            # Get the next step from the current agent
            from custom import execute_plan
            execution_log = await execute_plan(user_input, session_data)
            
            # If the execution log indicates we need more input
            if isinstance(execution_log, dict) and execution_log.get("status") == "need_input":
                session_data["current_step"] = {
                    "next_field": execution_log["next_field"],
                    "status": execution_log["status"],
                    "prompt": execution_log["prompt"]
                }
                return {
                    "status": "need_input",
                    "prompt": execution_log["prompt"],
                    "next_field": execution_log["next_field"],
                    "session_data": session_data
                }
            
            # If we've completed all steps
            return {
                "status": "complete",
                "response": execution_log,
                "session_data": session_data
            }
        except Exception as e:
            print(f"Error in process_user_input: {str(e)}")
            raise
    
    # If this is a new conversation, classify the input
    try:
        result = await classify_user_input(user_input)
        
        try:
            data = json.loads(result)
        except json.JSONDecodeError:
            if result.startswith("```json"):
                plan_text = result.lstrip("```json").rstrip("```").strip()
                data = json.loads(plan_text)
        
        if data["category"] == "greeting or general_conversation" or data["category"] == "general_question":
            return {
                "status": "complete",
                "response": data["response"],
                "session_data": session_data
            }
        elif data["category"] == "plan_required":
            # Call execute_plan from custom.py
            from custom import execute_plan
            execution_log = await execute_plan(user_input, session_data)
            
            # If the execution log indicates we need more input
            if isinstance(execution_log, dict) and execution_log.get("status") == "need_input":
                session_data["current_step"] = {
                    "next_field": execution_log["next_field"],
                    "status": execution_log["status"],
                    "prompt": execution_log["prompt"]
                }
                return {
                    "status": "need_input",
                    "prompt": execution_log["prompt"],
                    "next_field": execution_log["next_field"],
                    "session_data": session_data
                }
            
            # If we've completed all steps
            return {
                "status": "complete",
                "response": execution_log,
                "session_data": session_data
            }
        else:
            return {
                "status": "complete",
                "response": "Unknown category",
                "session_data": session_data
            }
    except Exception as e:
        print(f"Error in process_user_input: {str(e)}")
        raise

# Example usage (for testing)
if __name__ == "__main__":
    import asyncio
    async def test():
        response = await process_user_input("Hi, how are you today?")
        print(response)
    asyncio.run(test())