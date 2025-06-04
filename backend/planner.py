from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import SystemMessage, UserMessage, LLMMessage
from pydantic import BaseModel
from config import model_client
from appointment import appointment_agent
from doctor import doctor_agent
from clinical_recommendation import clinical_recommendation_agent
from insurance_verfication import insurance_verification_agent
from patient_intake import patient_intake_agent
from monitoring import monitoring_agent
from notification import notification_agent
import asyncio
from typing import List, Optional
from pprint import pprint
import re, json 
import inspect
import ast

agents = [appointment_agent, doctor_agent, insurance_verification_agent, monitoring_agent, notification_agent, patient_intake_agent, clinical_recommendation_agent]

class CallCollector(ast.NodeVisitor):
    def __init__(self):
        self.calls = []

    def visit_Call(self, node):
        func_node = node.func
        func_name = (
            func_node.id if isinstance(func_node, ast.Name)
            else func_node.attr if isinstance(func_node, ast.Attribute)
            else None
        )
        if func_name:
            self.calls.append(func_name)
        self.generic_visit(node)

class StepSchema(BaseModel):
    agent: str
    function: str
    nested_functions: List[str]

class PlanSchema(BaseModel):
    summary: str
    steps: List[StepSchema]

async def create_plan(user_query: str):
    agent_info_lines = ["Agents and tools:"]
    for agent in agents:
        tool_names = ", ".join([func._name for func in agent._tools])
        agent_info_lines.append(f"{agent.name} (tools: {tool_names})")
    agents_and_tools = "\n".join(agent_info_lines)

    prompt = await generate_prompt(user_query, agents_and_tools) 

    resp = await model_client.create([SystemMessage(content=prompt)])
    plan_text = resp.content.strip()

    match = re.search(r"<PLAN_START>(.*?)<PLAN_END>", plan_text, re.DOTALL)
    if match:
        json_str = match.group(1).strip()

        plan = json.loads(json_str)
        functions = [step["function"] for step in plan["steps"]]

        # print("Functions:", functions)
        tool_name_map = get_tool_name_map()
        plan = [(tool_name_map[fn][0], fn) for fn in functions if fn in tool_name_map]
        print(plan) 
        return plan
    else:
        print("Plan not found.")

async def generate_prompt(objective: str, agents_and_tools: str):
    prompt = f"""
    You are the Planner, an AI orchestrator that manages a group of AI agents to accomplish healthcare related tasks. Remember: You are bounded to stay inside the boundaries of healthcare related queries. Anything other than that is asked, respond that you are not capable of that.

    For the given objective, come up with a simple step-by-step plan.
    This plan should involve individual tasks that, if executed correctly, will yield the correct answer. Do not add any superfluous steps.
    The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.

    These actions are passed to the specific agent. Make sure the action contains all the information required for the agent to execute the task.

    Your objective is:
    {objective}

    The agents and their tools that you have access to are:
    {agents_and_tools}

    The first step of your plan should be to ask the user for any additional information required to progress the rest of steps planned.

    If it is a general healthcare industry related question like "Why would my doctor order a chest X-ray?" then just answer right away, you don't need to get into details of functions then.
    Other than that Only use the functions provided as part of your plan. If the task is not possible with the agents and tools provided and the task is of type that LLM can't answer it then create a step with the agent of type Exception and mark the overall status as completed. But if you can answer it then directly give the answer no need for exception in that case.
    Remember only the doctor agent can call the Clinical recommendation agent so if the function: generate_clinical_recommendations is called then the doctor agent should be called with function: review_patient_case and not the clinical recommendation agent because its part of the review_patient_case function.
    
    If the tools of Patient Intake Agent are called then the tool of Doctor agent should also be called: review_patient_case. 
    If the patient comes up with their details or say they are here then there is no need for appointment scheduling and consider that they have already booked an appointment.

    Do not add any steps from Monitoring or Notificatn agents.
    Do not add superfluous steps - only take the most direct path to the solution, with the minimum number of steps. Only do the minimum necessary to complete the goal.

    If there is a single function call that can directly solve the task, only generate a plan with a single step.

    When generating the action in the plan, frame the action as an instruction you are passing to the agent to execute. It should be a short, single sentence. Include the function to use. For example, "Patient (Jessica Smith)'s case needs to be reviewed. Agent: DoctorAgent Function: review_patient_case"

    Ensure the summary of the plan and the overall steps is less than 50 words. 

    You must prioritise using the provided functions to accomplish each step. First evaluate each and every function the agents have access too. Only if you cannot find a function needed to complete the task, and you have reviewed each and every function, and determined why each are not suitable, there are two options you can take when generating the plan.
    
    If a general Large Language Model CAN handle the step/required action, add a step to the plan with the action you believe would be needed, and add "EXCEPTION: No suitable function found. A generic LLM model is being used for this step." to the end of the action. Assign these steps to the GenericAgent. For example, if the task is to convert the following SQL into python code (SELECT * FROM employees;), and there is no function to convert SQL to python, write a step with the action "convert the following SQL into python code (SELECT * FROM employees;) EXCEPTION: No suitable function found. A generic LLM model is being used for this step." and assign it to the GenericAgent.
    First evaluate whether the step could be handled by a typical large language model, without any specialised functions but this needs to be related to healthcare.
    
    Limit the plan to 6 steps or less.
    Return the plan in this exact format:

    <PLAN_START>
    {{
    "summary": "short summary here",
    "steps": [
        {{
        "agent": "AgentName",
        "function": "FunctionName"
        }},
        {{
        "agent": "AgentName",
        "function": "FunctionName"
        }},
        rest of the functions....
        ...
    ]
    }}
    <PLAN_END>
    """

    return prompt

def check_nested_funcs(plan_text: List[str]):
    functions = plan_text
    # Collect all tool function names across agents
    tool_name_map = {}
    for agent in agents:
        for tool in agent._tools:
            func = getattr(tool, "func", getattr(tool, "_func", None))
            if func:
                tool_name_map[func.__name__] = (agent.name, tool._name)
                # print(func)

    lines = []
    for agent in agents:
        for tool in agent._tools:
            if tool._name in functions:
                lines.append(f"- {agent.name}: {tool._name}")
                try:
                    func = getattr(tool, "func", getattr(tool, "_func", None))
                    if func is None:
                        continue
                    src = inspect.getsource(func)
                    tree = ast.parse(src)
                    calls = []
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Call):
                            func_node = node.func
                            func_name = (
                                func_node.id if isinstance(func_node, ast.Name)
                                else func_node.attr if isinstance(func_node, ast.Attribute)
                                else None
                            )
                            if func_name and func_name in tool_name_map:
                                calls.append(func_name)
                    if calls:
                        unique_calls = sorted(set(calls))
                        lines.append(f"    * Calls agent tools: {', '.join(unique_calls)}")
                        plan_text.extend(unique_calls)
                except Exception as e:
                    print(f"Error parsing {tool._name}: {e}")

    return ("\n".join(lines))

def get_tool_name_map():
    tool_name_map = {}
    for agent in agents:
        for tool in agent._tools:
            func = getattr(tool, "func", getattr(tool, "_func", None))
            if func:
                tool_name_map[func.__name__] = (agent.name, tool._name, func)
    return (tool_name_map)

def resolve_function_sequence(start_funcs: List[str], tool_name_map: dict) -> List[tuple]:
    seen = set()
    ordered_sequence = []

    def dfs(func_name):
        if func_name not in tool_name_map or func_name in seen:
            return
        seen.add(func_name)

        agent_name, tool_name, func = tool_name_map[func_name]

        try:
            src = inspect.getsource(func)
            tree = ast.parse(src)
            collector = CallCollector()
            collector.visit(tree)

            ordered_sequence.append((agent_name, tool_name))
            for nested in collector.calls:
                dfs(nested)

        except Exception as e:
            print(f"Error parsing {func_name}: {e}")

    for func_name in start_funcs:
        dfs(func_name)

    return ordered_sequence

# pprint(asyncio.run(create_plan('i want to book an appointment and get my insurance checked.')))

planner_agent = AssistantAgent(
    name="PlannerAgent",
    model_client=model_client,
    system_message="You are a planner.",
    tools=[create_plan],
)
