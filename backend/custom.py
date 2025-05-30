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
    if session_data is None:
        session_data = {}

    if "current_step" in session_data:
        try:
            current_step = session_data.get("current_step", {})
            if "agent_info" in current_step:
                agent_name, fn_name = current_step["agent_info"]
            else:
                if not session_data.get("plan"):
                    session_data["plan"] = await create_plan(user_query)
                agent_name, fn_name = session_data["plan"][0]

            agent = agent_lookup.get(agent_name)
            if not agent:
                raise RuntimeError(f"Unknown agent {agent_name} in plan")

            tool = get_tool(agent, fn_name)
            func = tool._func
            
            if "last_answer" in session_data and session_data.get("current_step", {}).get("agent_info", [""])[0] != agent_name:
                session_data.pop("last_answer")

            result = await func(session_data=session_data)

            if isinstance(result, dict) and result.get("status") == "need_input":
                response_data = {
                    "status": result["status"],
                    "prompt": result["prompt"],
                    "next_field": result["next_field"],
                    "session_data": {
                        "current_step": {
                            "agent_info": [agent_name, fn_name],
                            "status": result["status"],
                            "prompt": result["prompt"],
                            "next_field": result["next_field"]
                        },
                        "plan": session_data.get("plan", []),
                        **{k: v for k, v in session_data.items() if k not in ["current_step", "plan"]}
                    }
                }
                return response_data
        except Exception as e:
            print(f"Error in execute_plan: {str(e)}")
            raise

        session_data.pop("current_step", None)

        if "plan" not in session_data or not session_data["plan"]:
            session_data["plan"] = await create_plan(user_query)
        
        current_step_index = next((i for i, (a, f) in enumerate(session_data["plan"]) if a == agent_name and f == fn_name), -1)
        
        if current_step_index < len(session_data["plan"]) - 1:
            next_agent_name, next_fn_name = session_data["plan"][current_step_index + 1]
            next_agent = agent_lookup.get(next_agent_name)
            if not next_agent:
                raise RuntimeError(f"Unknown agent {next_agent_name} in plan")
            
            next_tool = get_tool(next_agent, next_fn_name)
            next_func = next_tool._func
            
            print(f"\n>> Moving to next step: {next_agent_name}.{next_fn_name}()")

            session_data["current_step"] = {
                "agent_info": [next_agent_name, next_fn_name],
                "status": "pending"
            }
            return await execute_plan(user_query, session_data)

        return {
            "status": "complete",
            "data": result,
            "session_data": session_data
        }

    execution_log = []
    raw_plan = await create_plan(user_query)
    session_data["plan"] = raw_plan
    step_index = 0

    while step_index < len(raw_plan):
        agent_name, fn_name = raw_plan[step_index]
        agent = agent_lookup.get(agent_name)
        if not agent:
            raise RuntimeError(f"Unknown agent {agent_name} in plan")

        tool = get_tool(agent, fn_name)
        func = tool._func

        print(f"\n>> STEP {step_index + 1}/{len(raw_plan)}: {agent_name}.{fn_name}()")

        try:
            result = await func(session_data=session_data)

            if isinstance(result, dict) and result.get("status") == "need_input":
                session_data["current_step"] = {
                    "agent_info": (agent_name, fn_name),
                    **result
                }

                response_data = {
                    "status": result["status"],
                    "prompt": result["prompt"],
                    "next_field": result["next_field"],
                    "session_data": {
                        "current_step": {
                            "agent_info": [agent_name, fn_name],
                            "status": result["status"],
                            "prompt": result["prompt"],
                            "next_field": result["next_field"]
                        },
                        "plan": session_data.get("plan", []),
                        **{k: v for k, v in session_data.items() if k not in ["current_step", "plan"]}
                    }
                }
                return response_data
                
            print(f"Result: {result}")
            execution_log.append(result)
            step_index += 1

        except Exception as e:
            print(f"Error on step {step_index + 1}: {e}")
            raise e

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