# import inspect
# from typing import Any, Dict, List

# from planner import create_plan
# from appointment import appointment_agent
# from insurance_verfication import insurance_verification_agent
# from notification import notification_agent
# from patient_intake import patient_intake_agent
# from doctor import doctor_agent
# from clinical_recommendation import clinical_recommendation_agent
# from monitoring import monitoring_agent

# import asyncio

# agent_lookup = {
#     "PatientIntakeAgent": patient_intake_agent,
#     "DoctorAgent": doctor_agent,
#     "NotificationAgent": notification_agent,
#     "AppointmentAgent": appointment_agent,
#     "ClinicalRecommendationAgent": clinical_recommendation_agent,
#     "MonitoringAgent": monitoring_agent,
#     "InsuranceVerificationAgent": insurance_verification_agent,
# }

# def get_tool(agent, fn_name):
#     for tool in agent._tools:
#         if tool._name == fn_name:
#             return tool
#     raise KeyError(f"{agent.name} has no tool {fn_name}")

# async def execute_plan(user_query: str, session_data: dict = None) -> List[Dict[str, Any]]:
#     if session_data is None:
#         session_data = {}

#     if "current_step" in session_data:
#         try:
#             current_step = session_data.get("current_step", {})
#             if "agent_info" in current_step:
#                 agent_name, fn_name = current_step["agent_info"]
#             else:
#                 if not session_data.get("plan"):
#                     session_data["plan"] = await create_plan(user_query)
#                 agent_name, fn_name = session_data["plan"][0]

#             agent = agent_lookup.get(agent_name)
#             if not agent:
#                 raise RuntimeError(f"Unknown agent {agent_name} in plan")

#             tool = get_tool(agent, fn_name)
#             func = tool._func
            
#             if "last_answer" in session_data and session_data.get("current_step", {}).get("agent_info", [""])[0] != agent_name:
#                 session_data.pop("last_answer")

#             result = await func(session_data=session_data)

#             if isinstance(result, dict) and result.get("status") == "need_input":
#                 response_data = {
#                     "status": result["status"],
#                     "prompt": result["prompt"],
#                     "next_field": result["next_field"],
#                     "session_data": {
#                         "current_step": {
#                             "agent_info": [agent_name, fn_name],
#                             "status": result["status"],
#                             "prompt": result["prompt"],
#                             "next_field": result["next_field"]
#                         },
#                         "plan": session_data.get("plan", []),
#                         **{k: v for k, v in session_data.items() if k not in ["current_step", "plan"]}
#                     }
#                 }
#                 return response_data
#         except Exception as e:
#             print(f"Error in execute_plan: {str(e)}")
#             raise

#         session_data.pop("current_step", None)

#         if "plan" not in session_data or not session_data["plan"]:
#             session_data["plan"] = await create_plan(user_query)
        
#         current_step_index = next((i for i, (a, f) in enumerate(session_data["plan"]) if a == agent_name and f == fn_name), -1)
        
#         if current_step_index < len(session_data["plan"]) - 1:
#             next_agent_name, next_fn_name = session_data["plan"][current_step_index + 1]
#             next_agent = agent_lookup.get(next_agent_name)
#             if not next_agent:
#                 raise RuntimeError(f"Unknown agent {next_agent_name} in plan")
            
#             next_tool = get_tool(next_agent, next_fn_name)
#             next_func = next_tool._func
            
#             print(f"\n>> Moving to next step: {next_agent_name}.{next_fn_name}()")

#             session_data["current_step"] = {
#                 "agent_info": [next_agent_name, next_fn_name],
#                 "status": "pending"
#             }
#             return await execute_plan(user_query, session_data)

#         return {
#             "status": "complete",
#             "data": result,
#             "session_data": session_data
#         }

#     execution_log = []
#     raw_plan = await create_plan(user_query)
#     session_data["plan"] = raw_plan
#     step_index = 0

#     while step_index < len(raw_plan):
#         agent_name, fn_name = raw_plan[step_index]
#         agent = agent_lookup.get(agent_name)
#         if not agent:
#             raise RuntimeError(f"Unknown agent {agent_name} in plan")

#         tool = get_tool(agent, fn_name)
#         func = tool._func

#         print(f"\n>> STEP {step_index + 1}/{len(raw_plan)}: {agent_name}.{fn_name}()")

#         try:
#             result = await func(session_data=session_data)

#             if isinstance(result, dict) and result.get("status") == "need_input":
#                 session_data["current_step"] = {
#                     "agent_info": (agent_name, fn_name),
#                     **result
#                 }

#                 response_data = {
#                     "status": result["status"],
#                     "prompt": result["prompt"],
#                     "next_field": result["next_field"],
#                     "session_data": {
#                         "current_step": {
#                             "agent_info": [agent_name, fn_name],
#                             "status": result["status"],
#                             "prompt": result["prompt"],
#                             "next_field": result["next_field"]
#                         },
#                         "plan": session_data.get("plan", []),
#                         **{k: v for k, v in session_data.items() if k not in ["current_step", "plan"]}
#                     }
#                 }
#                 return response_data
                
#             print(f"Result: {result}")
#             execution_log.append(result)
#             step_index += 1

#         except Exception as e:
#             print(f"Error on step {step_index + 1}: {e}")
#             raise e

#     if execution_log:
#         final_result = execution_log[-1]
#         if isinstance(final_result, dict):
#             final_result["session_data"] = {
#                 "plan": session_data.get("plan", []),
#                 **{k: v for k, v in session_data.items() if k not in ["current_step", "plan"]}
#             }
#         return final_result
#     return execution_log

# if __name__ == "__main__":
#     results = asyncio.run(execute_plan("i want to get my case reviewed"))
#     print("\n=== All steps complete ===")
#     for i, r in enumerate(results, 1):
#         print(f"Step {i} output → {r}") 










# from typing import Any, Dict, List

# from planner import create_plan
# from appointment import appointment_agent
# from insurance_verfication import insurance_verification_agent
# from notification import notification_agent
# from patient_intake import patient_intake_agent
# from doctor import doctor_agent
# from clinical_recommendation import clinical_recommendation_agent
# from monitoring import monitoring_agent

# import asyncio

# agent_lookup = {
#     "PatientIntakeAgent": patient_intake_agent,
#     "DoctorAgent": doctor_agent,
#     "NotificationAgent": notification_agent,
#     "AppointmentAgent": appointment_agent,
#     "ClinicalRecommendationAgent": clinical_recommendation_agent,
#     "MonitoringAgent": monitoring_agent,
#     "InsuranceVerificationAgent": insurance_verification_agent,
# }

# def get_tool(agent, fn_name):
#     for tool in agent._tools:
#         if tool._name == fn_name:
#             return tool
#     raise KeyError(f"{agent.name} has no tool {fn_name}")

# async def execute_plan(user_query: str, session_data: dict = None) -> List[Dict[str, Any]]:
#     if session_data is None:
#         session_data = {}

#     if "current_step" in session_data:
#         try:
#             current_step = session_data.get("current_step", {})
#             if "agent_info" in current_step:
#                 agent_name, fn_name = current_step["agent_info"]
#             else:
#                 if not session_data.get("plan"):
#                     session_data["plan"] = await create_plan(user_query)
#                 agent_name, fn_name = session_data["plan"][0]

#             agent = agent_lookup.get(agent_name)
#             if not agent:
#                 raise RuntimeError(f"Unknown agent {agent_name} in plan")

#             tool = get_tool(agent, fn_name)
#             func = tool._func
            
#             if "last_answer" in session_data and session_data.get("current_step", {}).get("agent_info", [""])[0] != agent_name:
#                 session_data.pop("last_answer")

#             result = await func(session_data=session_data)

#             if isinstance(result, dict) and result.get("status") == "need_input":
#                 print("Custom.py: Received result from agent:", result)  # Debug log
#                 # Get any file upload related flags from the result
#                 file_upload_flags = {
#                     "requiresFileUpload": result.get("requiresFileUpload", False),
#                     "type": result.get("type"),
#                     "input_type": result.get("input_type"),
#                     "accept": result.get("accept")
#                 }
                
#                 response_data = {
#                     "status": result["status"],
#                     "prompt": result["prompt"],
#                     "next_field": result["next_field"],
#                     **file_upload_flags,  # Add flags at root level
#                     "session_data": {
#                         "current_step": {
#                             "agent_info": [agent_name, fn_name],
#                             **result  # Keep all original data in current_step
#                         },
#                         "plan": session_data.get("plan", []),
#                         **{k: v for k, v in session_data.items() if k not in ["current_step", "plan"]}
#                     }
#                 }
#                 print("Custom.py: Sending response:", response_data)  # Debug log
#                 return response_data
#         except Exception as e:
#             print(f"Error in execute_plan: {str(e)}")
#             raise

#         session_data.pop("current_step", None)

#         if "plan" not in session_data or not session_data["plan"]:
#             session_data["plan"] = await create_plan(user_query)
        
#         current_step_index = next((i for i, (a, f) in enumerate(session_data["plan"]) if a == agent_name and f == fn_name), -1)
        
#         if current_step_index < len(session_data["plan"]) - 1:
#             next_agent_name, next_fn_name = session_data["plan"][current_step_index + 1]
#             next_agent = agent_lookup.get(next_agent_name)
#             if not next_agent:
#                 raise RuntimeError(f"Unknown agent {next_agent_name} in plan")
            
#             next_tool = get_tool(next_agent, next_fn_name)
#             next_func = next_tool._func
            
#             print(f"\n>> Moving to next step: {next_agent_name}.{next_fn_name}()")

#             session_data["current_step"] = {
#                 "agent_info": [next_agent_name, next_fn_name],
#                 "status": "pending"
#             }
#             return await execute_plan(user_query, session_data)

#         return {
#             "status": "complete",
#             "data": result,
#             "session_data": session_data
#         }

#     execution_log = []
#     raw_plan = await create_plan(user_query)
#     session_data["plan"] = raw_plan
#     step_index = 0

#     while step_index < len(raw_plan):
#         agent_name, fn_name = raw_plan[step_index]
#         agent = agent_lookup.get(agent_name)
#         if not agent:
#             raise RuntimeError(f"Unknown agent {agent_name} in plan")

#         tool = get_tool(agent, fn_name)
#         func = tool._func

#         print(f"\n>> STEP {step_index + 1}/{len(raw_plan)}: {agent_name}.{fn_name}()")

#         try:
#             result = await func(session_data=session_data)

#             if isinstance(result, dict) and result.get("status") == "need_input":
#                 print("Custom.py: Received result from agent:", result)  # Debug log
#                 session_data["current_step"] = {
#                     "agent_info": (agent_name, fn_name),
#                     **result
#                 }

#                 # Get any file upload related flags from the result
#                 file_upload_flags = {
#                     "requiresFileUpload": result.get("requiresFileUpload", False),
#                     "type": result.get("type"),
#                     "input_type": result.get("input_type"),
#                     "accept": result.get("accept")
#                 }

#                 response_data = {
#                     "status": result["status"],
#                     "prompt": result["prompt"],
#                     "next_field": result["next_field"],
#                     **file_upload_flags,  # Add flags at root level
#                     "session_data": {
#                         "current_step": {
#                             "agent_info": [agent_name, fn_name],
#                             **result  # Keep all original data in current_step
#                         },
#                         "plan": session_data.get("plan", []),
#                         **{k: v for k, v in session_data.items() if k not in ["current_step", "plan"]}
#                     }
#                 }
#                 print("Custom.py: Sending response:", response_data)  # Debug log
#                 return response_data
                
#             print(f"Result: {result}")
#             execution_log.append(result)
#             step_index += 1

#         except Exception as e:
#             print(f"Error on step {step_index + 1}: {e}")
#             raise e

#     if execution_log:
#         final_result = execution_log[-1]
#         if isinstance(final_result, dict):
#             final_result["session_data"] = {
#                 "plan": session_data.get("plan", []),
#                 **{k: v for k, v in session_data.items() if k not in ["current_step", "plan"]}
#             }
#         return final_result
#     return execution_log 


import inspect
from typing import Any, Dict, List

from planner import create_plan
from appointment import appointment_agent
from insurance_verfication import insurance_verification_agent
from notification import notification_agent
from patient_intake import patient_intake_agent
from doctor import doctor_agent
from clinical_recommendation import clinical_recommendation_agent
from monitoring import monitoring_agent

import asyncio

agent_lookup = {
    "PatientIntakeAgent": patient_intake_agent,
    "DoctorAgent": doctor_agent,
    "NotificationAgent": notification_agent,
    "AppointmentAgent": appointment_agent,
    "ClinicalRecommendationAgent": clinical_recommendation_agent,
    "MonitoringAgent": monitoring_agent,
    "InsuranceVerificationAgent": insurance_verification_agent,
}

def get_tool(agent, fn_name):
    for tool in agent._tools:
        if tool._name == fn_name:
            return tool
    raise KeyError(f"{agent.name} has no tool {fn_name}")

async def execute_plan(user_query: str, session_data: dict = None) -> List[Dict[str, Any]]:
    print("Custom.py: Starting execute_plan")
    print("Custom.py: User query:", user_query)
    print("Custom.py: Initial session data:", session_data)
    
    if session_data is None:
        session_data = {}

    if "current_step" in session_data:
        try:
            print("Custom.py: Continuing with current step")
            current_step = session_data.get("current_step", {})
            if "agent_info" in current_step:
                agent_name, fn_name = current_step["agent_info"]
                print(f"Custom.py: Using agent info from current step: {agent_name}.{fn_name}")
            else:
                if not session_data.get("plan"):
                    print("Custom.py: No plan found, creating new plan")
                    session_data["plan"] = await create_plan(user_query)
                agent_name, fn_name = session_data["plan"][0]
                print(f"Custom.py: Using first step from plan: {agent_name}.{fn_name}")

            agent = agent_lookup.get(agent_name)
            if not agent:
                raise RuntimeError(f"Unknown agent {agent_name} in plan")

            tool = get_tool(agent, fn_name)
            func = tool._func
            
            if "last_answer" in session_data and session_data.get("current_step", {}).get("agent_info", [""])[0] != agent_name:
                session_data.pop("last_answer")

            print(f"Custom.py: Calling {agent_name}.{fn_name}")
            result = await func(session_data=session_data)
            print(f"Custom.py: Received result from {agent_name}.{fn_name}:", result)

            # Pass through show_message status
            if isinstance(result, dict) and result.get("status") == "show_message":
                print("Custom.py: Handling show_message status")
                # If we don't have a plan yet, create one
                if "plan" not in session_data:
                    print("Custom.py: No plan found, creating new plan for show_message")
                    session_data["plan"] = await create_plan(user_query)
                
                response = {
                    **result,
                    "session_data": {
                        "current_step": {
                            "agent_info": [agent_name, fn_name],
                            **result
                        },
                        "plan": session_data["plan"],
                        **{k: v for k, v in session_data.items() if k not in ["current_step", "plan"]}
                    }
                }
                print("Custom.py: Returning show_message response:", response)
                return response

            if isinstance(result, dict) and result.get("status") == "need_input":
                print("Custom.py: Handling need_input status")
                # Get any file upload related flags from the result
                file_upload_flags = {
                    "requiresFileUpload": result.get("requiresFileUpload", False),
                    "type": result.get("type"),
                    "input_type": result.get("input_type"),
                    "accept": result.get("accept")
                }
                
                # Create a clean version of the current step without session_data
                current_step = {
                    "agent_info": [agent_name, fn_name],
                    "status": result["status"],
                    "prompt": result["prompt"],
                    "next_field": result["next_field"],
                    "requiresFileUpload": result.get("requiresFileUpload", False),
                    "type": result.get("type"),
                    "input_type": result.get("input_type"),
                    "accept": result.get("accept")
                }
                
                response_data = {
                    "status": result["status"],
                    "prompt": result["prompt"],
                    "next_field": result["next_field"],
                    **file_upload_flags,
                    "session_data": {
                        "current_step": current_step,
                        "plan": session_data.get("plan", []),
                        **{k: v for k, v in session_data.items() if k not in ["current_step", "plan"]}
                    }
                }
                print("Custom.py: Returning need_input response:", response_data)
                return response_data

        except Exception as e:
            print(f"Error in execute_plan: {str(e)}")
            raise

        print("Custom.py: Step completed, moving to next step")
        session_data.pop("current_step", None)

        if "plan" not in session_data or not session_data["plan"]:
            print("Custom.py: No plan found after step completion, creating new plan")
            session_data["plan"] = await create_plan(user_query)
        
        current_step_index = next((i for i, (a, f) in enumerate(session_data["plan"]) if a == agent_name and f == fn_name), -1)
        
        if current_step_index < len(session_data["plan"]) - 1:
            next_agent_name, next_fn_name = session_data["plan"][current_step_index + 1]
            print(f"Custom.py: Moving to next step: {next_agent_name}.{next_fn_name}")
            next_agent = agent_lookup.get(next_agent_name)
            if not next_agent:
                raise RuntimeError(f"Unknown agent {next_agent_name} in plan")
            
            next_tool = get_tool(next_agent, next_fn_name)
            next_func = next_tool._func

            session_data["current_step"] = {
                "agent_info": [next_agent_name, next_fn_name],
                "status": "pending"
            }
            return await execute_plan(user_query, session_data)

        print("Custom.py: All steps completed")
        return {
            "status": "complete",
            "data": result,
            "session_data": session_data
        }

    print("Custom.py: Starting new plan execution")
    execution_log = []
    raw_plan = await create_plan(user_query)
    print("Custom.py: Created plan:", raw_plan)
    session_data["plan"] = raw_plan
    step_index = 0

    while step_index < len(raw_plan):
        agent_name, fn_name = raw_plan[step_index]
        print(f"Custom.py: Executing step {step_index + 1}: {agent_name}.{fn_name}")
        agent = agent_lookup.get(agent_name)
        if not agent:
            raise RuntimeError(f"Unknown agent {agent_name} in plan")

        tool = get_tool(agent, fn_name)
        func = tool._func

        try:
            result = await func(session_data=session_data)
            print(f"Custom.py: Received result from {agent_name}.{fn_name}:", result)

            # Pass through show_message status
            if isinstance(result, dict) and result.get("status") == "show_message":
                print("Custom.py: Handling show_message status in plan")
                # Create a clean version of the current step without session_data
                current_step = {
                    "agent_info": [agent_name, fn_name],
                    "status": result["status"],
                    "message": result["message"],
                    "next_field": result.get("next_field")
                }
                
                response = {
                    **result,
                    "session_data": {
                        "current_step": current_step,
                        "plan": session_data["plan"],
                        **{k: v for k, v in session_data.items() if k not in ["current_step", "plan"]}
                    }
                }
                print("Custom.py: Returning show_message response from plan:", response)
                return response

            if isinstance(result, dict) and result.get("status") == "need_input":
                print("Custom.py: Handling need_input status in plan")
                session_data["current_step"] = {
                    "agent_info": (agent_name, fn_name),
                    **result
                }

                # Get any file upload related flags from the result
                file_upload_flags = {
                    "requiresFileUpload": result.get("requiresFileUpload", False),
                    "type": result.get("type"),
                    "input_type": result.get("input_type"),
                    "accept": result.get("accept")
                }

                response_data = {
                    "status": result["status"],
                    "prompt": result["prompt"],
                    "next_field": result["next_field"],
                    **file_upload_flags,
                    "session_data": {
                        "current_step": {
                            "agent_info": [agent_name, fn_name],
                            **result
                        },
                        "plan": session_data.get("plan", []),
                        **{k: v for k, v in session_data.items() if k not in ["current_step", "plan"]}
                    }
                }
                print("Custom.py: Returning need_input response from plan:", response_data)
                return response_data
                
            print(f"Custom.py: Step {step_index + 1} completed successfully")
            execution_log.append(result)
            step_index += 1

        except Exception as e:
            print(f"Error on step {step_index + 1}: {e}")
            raise e

    print("Custom.py: All plan steps completed")
    if execution_log:
        final_result = execution_log[-1]
        if isinstance(final_result, dict):
            final_result["session_data"] = {
                "plan": session_data.get("plan", []),
                **{k: v for k, v in session_data.items() if k not in ["current_step", "plan"]}
            }
        return final_result
    return execution_log

if __name__ == "__main__":
    results = asyncio.run(execute_plan("i want to get my case reviewed"))
    print("\n=== All steps complete ===")
    for i, r in enumerate(results, 1):
        print(f"Step {i} output → {r}")