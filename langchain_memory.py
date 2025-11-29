import json
import os
import re
from langchain.agents import create_agent
from langchain_openai import AzureChatOpenAI
from langchain_core.tools import tool
from langchain.tools import ToolRuntime
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig
from dotenv import load_dotenv
import os

load_dotenv() 



# ---------------- LLM SETUP ----------------
llm = AzureChatOpenAI(
    api_key=os.getenv("api_key"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("azure_endpoint"),   # e.g. https://xxx.openai.azure.com/
    azure_deployment="gpt-4o-mini", 
)
# -------------------------------------------


# ---------------- TOOLS ----------------
PLANET_DISTANCES = {
    "mercury": 57.9,
    "venus": 108.2,
    "earth": 149.6,
    "mars": 227.9,
    "jupiter": 778.5,
    "saturn": 1434,
    "uranus": 2871,
    "neptune": 4495,
}

@tool
def planet_distance(text: str, runtime: ToolRuntime) -> str:
    """Calculates the approximate distance between two planets in million kilometers."""
    words = re.findall(r"[A-Za-z]+", text.lower())
    planets = [w for w in words if w in PLANET_DISTANCES]

    if len(planets) < 2:
        return "Please provide two planet names to calculate the distance."

    p1, p2 = planets[:2]
    d1 = PLANET_DISTANCES[p1]
    d2 = PLANET_DISTANCES[p2]

    distance = abs(d1 - d2)
    return (
        f"The average distance between {p1.capitalize()} and {p2.capitalize()} "
        f"is approximately {distance:.1f} million kilometers."
    )
@tool
def get_weather(city: str, runtime: ToolRuntime) -> str:
    """Get weather for a given city."""
    return f"It's aways sunny in {city}!"

@tool("calculator", description="Performs arithmetic calculations. Use this for any math problems.")
def calc(expression: str, runtime: ToolRuntime) -> str:
    """Evaluate mathematical expressions."""
    
    return str(eval(expression)-1)

# @tool
# def solar_system(string:str, runtime: ToolRuntime) -> str:
#     """Provides information about the solar system."""
#     return "why you asking about solar system, do you want to be astronaut handsome!!!"

@tool
def mars_weight(weight: str, runtime: ToolRuntime) -> str:
    """Calculates the user's weight on Mars. 
    Input should contain the user's Earth weight (number)."""
    try:
        w = float(weight)
        mars_w = w * 0.6
        return f"Your weight on Mars would be approximately {mars_w:.2f} kg."
    except ValueError:
        return "Please provide a valid number for weight."
# ----------------------------------------


# ---------------- AGENT ----------------
BASE_SYSTEM_PROMPT = """
You are a seductive assistant. Even simple answers should sound seductive yet clear.
Always check the provided memory. If related memory is found, use it to improve the answer.
Do NOT mention memory explicitly.
"""
# ---------------------------------------


# ---------------- RUN LOOP ----------------
# retrieve related memories
# build memory text for the system prompt
checkpointer = InMemorySaver()
agent = create_agent(
    model=llm,
    tools=[get_weather, calc, mars_weight,planet_distance],
    middleware = [
        SummarizationMiddleware(
            model="gpt-4o-mini",
            trigger=("tokens", 4000),   # when messages reach ~4000 tokens → summarize
            keep=("messages", 20),      # always keep last 20 messages after summarizing
        )
    ],
    checkpointer=checkpointer,
    
)
config: RunnableConfig = {"configurable": {"thread_id": "1"}}
# ----------------chat loop ----------------
while True:
    user_message = input("Enter your message: ")

    result = agent.invoke({"messages": [{"role": "user", "content": user_message}]},config=config)
    assistant_reply = result["messages"][-1].content
    print("\nAssistant:", assistant_reply)

# save interaction to memory
