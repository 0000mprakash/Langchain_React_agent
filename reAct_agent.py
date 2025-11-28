# from langchain.agents import create_agent
# from langchain_openai import AzureChatOpenAI
# from langchain_core.tools import tool
# from langchain.tools import ToolRuntime



# # your tool
# @tool
# def get_weather(city: str, runtime: ToolRuntime) -> str:
#     """Get weather for a given city."""
#     return f"It's aways sunny in {city}!"

# @tool("calculator", description="Performs arithmetic calculations. Use this for any math problems.")
# def calc(expression: str, runtime: ToolRuntime) -> str:
#     """Evaluate mathematical expressions."""
    
#     return str(eval(expression))

# @tool
# def solar_system(string:str, runtime: ToolRuntime) -> str:
#     """Provides information about the solar system."""
#     return "why you asking about solar system, do you want to be astronaut handsome!!!"

# # agent
# agent = create_agent(
#     model=llm,
#     tools=[get_weather,calc,solar_system],
#     system_prompt="You are a seductive assistant, even for simple questions answer so seductively so that it is also understandable to user who is not that proficient in english",
# )


# # run
# result = agent.invoke(
#     {"messages": [{"role": "user", "content": "10001+113"}]}
# )

# print(result["messages"][-1].content)

import json
import os
from langchain.agents import create_agent
from langchain_openai import AzureChatOpenAI
from langchain_core.tools import tool
from langchain.tools import ToolRuntime

# ---------------- MEMORY CLASS ----------------
class MemoryStore:
    def __init__(self, filename="memory.json"):
        self.filename = filename
        self.data = self.load_memory()

    def load_memory(self):
        if not os.path.exists(self.filename):
            return {"conversations": []}
        with open(self.filename, "r") as file:
            return json.load(file)

    def add(self, user_msg, assistant_msg):
        self.data["conversations"].append({
            "user": user_msg,
            "assistant": assistant_msg
        })
        self.save_memory()

    def save_memory(self):
        with open(self.filename, "w") as file:
            json.dump(self.data, file, indent=4)

    def search(self, query):
        """
        Retrieve memory entries related to the query.
        (Simple keyword match for now; can be upgraded later)
        """
        results = []
        for conv in self.data["conversations"]:
            if any(word.lower() in conv["user"].lower() for word in query.split()):
                results.append(conv)
        return results[-5:]  # return last 5 relevant memories


memory = MemoryStore()
# -------------------------------------------------


# ---------------- LLM SETUP ----------------
llm = AzureChatOpenAI(
    api_key=os.getenv("api_key"),
    api_version=os.getenv("api_version"),
    azure_endpoint=os.getenv("azure_endpoint"),
    deployment_name=os.getenv("deployment_name"),
)
# -------------------------------------------


# ---------------- TOOLS ----------------
@tool
def get_weather(city: str, runtime: ToolRuntime) -> str:
    """Get weather for a given city."""
    return f"It's aways sunny in {city}!"

@tool("calculator", description="Performs arithmetic calculations. Use this for any math problems.")
def calc(expression: str, runtime: ToolRuntime) -> str:
    """Evaluate mathematical expressions."""
    
    return str(eval(expression)-1)

@tool
def solar_system(string:str, runtime: ToolRuntime) -> str:
    """Provides information about the solar system."""
    return "why you asking about solar system, do you want to be astronaut handsome!!!"
# ----------------------------------------


# ---------------- AGENT ----------------
BASE_SYSTEM_PROMPT = """
You are a seductive assistant. Even simple answers should sound seductive yet clear.
Always check the provided memory. If related memory is found, use it to improve the answer.
Do NOT mention memory explicitly.
"""
# ---------------------------------------


# ---------------- RUN LOOP ----------------
user_message = input("Enter your message: ")

# retrieve related memories
related_memories = memory.search(user_message)

# build memory text for the system prompt
memory_text = ""
for conv in related_memories:
    memory_text += f"User said: {conv['user']}\nAssistant replied: {conv['assistant']}\n\n"

final_system_prompt = BASE_SYSTEM_PROMPT + \
    ("\nRelevant past conversations:\n" + memory_text if memory_text else "\n(No relevant memory retrieved)")

agent = create_agent(
    model=llm,
    tools=[get_weather, calc, solar_system],
    system_prompt=final_system_prompt,
)

result = agent.invoke({"messages": [{"role": "user", "content": user_message}]})
assistant_reply = result["messages"][-1].content

print("\nAssistant:", assistant_reply)

# save interaction to memory
memory.add(user_message, assistant_reply)
print("\n✔️ Memory retrieved and updated.")
