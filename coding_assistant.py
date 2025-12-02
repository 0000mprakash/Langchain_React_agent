import subprocess
from langchain.agents import create_agent
from langchain_openai import AzureChatOpenAI
# from langchain.tools import Tool
from langchain_core.tools import tool
import subprocess
# Let the LLM produce the modified version
from langchain_core.messages import HumanMessage
from langchain_openai import AzureChatOpenAI
# from tavily import TavilyClient
import yt_dlp
from typing import List
import webbrowser
from dotenv import load_dotenv
import os
import requests
import youtube_dl  # Free Python library for downloading YouTube videos

load_dotenv() 

#-----------------Tools Definitions-----------------
@tool
def modify_file(path: str, instructions: str) -> str:
    """
    Safely modify an existing file using LLM-generated edits.

    - Prevents ``` code fences from being written into the file.
    - Validates the model’s output.
    - Ensures only raw code is saved.
    - Provides robust error messaging.
    """
    import os

    # ------- Helpers -------
    def strip_code_fences(text: str) -> str:
        """Remove Markdown fences like ``` or ```python from model output."""
        text = text.strip()

        # Remove leading fence
        if text.startswith("```"):
            text = text.split("\n", 1)[1]

        # Remove trailing fence
        if text.endswith("```"):
            text = text.rsplit("\n", 1)[0]

        return text.strip()

    # ------------------------

    if not os.path.exists(path):
        return f"Error: File not found → {path}"

    try:
        # Read original code
        with open(path, "r") as f:
            original = f.read()

        # ---------- LLM CALL ----------
        from langchain_core.messages import HumanMessage
        from langchain_openai import AzureChatOpenAI

        llm = AzureChatOpenAI(
            api_key=os.getenv("api_key"),
            api_version="2024-02-01",
            azure_endpoint=os.getenv("azure_endpoint"),
            azure_deployment="gpt-4o-mini",
        )

        prompt = f"""
You are a code-editing engine that outputs ONLY raw code.

DO NOT:
- Add ``` or ```python fences.
- Add explanations, summaries, comments, or metadata.
- Add "Here is your updated file:".
- Wrap the code in any formatting.

Your task:
Modify the following file EXACTLY as instructed, returning ONLY the full, final code of the file.

----- ORIGINAL FILE START -----
{original}
----- ORIGINAL FILE END -----

----- INSTRUCTIONS -----
{instructions}
----- END INSTRUCTIONS -----

Return ONLY the modified file content. No fences. No prose.
"""

        response = llm.invoke([HumanMessage(content=prompt)]).content
        modified = strip_code_fences(response)

        # Validate model output
        if not modified or modified.strip() == "":
            return "Error: LLM returned empty output — file NOT modified."

        # Safety: avoid accidentally deleting entire file unless asked
        if len(modified.strip()) < 5:
            return "Error: Output suspiciously small — refusing to overwrite file."

        # ---------- Write the modified file safely ----------
        with open(path, "w") as f:
            f.write(modified)

        return f"File modified successfully → {path}"

    except Exception as e:
        return f"Error modifying file: {str(e)}"



@tool
def write_file(path: str, content: str) -> str:
    """
    Create (if needed) and write content to a file.
    """
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    with open(path, "w") as f:
        f.write(content)

    return f"File created/written successfully → {path}"

@tool
def run_python(path: str) -> str:
    """
    Execute a Python file and return output or errors.
    Input: path of file to execute
    """
    result = subprocess.run(["python", path], capture_output=True, text=True)
    return result.stdout or result.stderr

@tool
def list_files_with_query(query: str) -> List[str]:
    """
    List all files in the current directory that contain the query string in their names.
    Input: query string to search for in file names.
    Output: List of file names containing the query string.
    """
    try:
        # Get the current working directory
        current_directory = os.getcwd()

        # List all files in the current directory
        files_in_directory = os.listdir(current_directory)

        # Filter files that contain the query string in their names
        matching_files = [file for file in files_in_directory if query.lower() in file.lower()]

        if not matching_files:
            return [f"No files found with '{query}' in the name."]

        return matching_files

    except Exception as e:
        return [f"Error searching for files: {str(e)}"]

    
@tool
def play_top_youtube_video(query: str) -> str:
    """
    Search YouTube using yt-dlp and play the first video result.
    Input: search query string.
    Output: URL of the video played.
    """
    try:
        # yt-dlp search configuration
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "extract_flat": "in_playlist",  # do not download, only get metadata
            "default_search": "ytsearch1",  # '1' means: return the first match
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(query, download=False)

        if "entries" not in result or len(result["entries"]) == 0:
            return f"No YouTube result found for: {query}"

        # First video entry
        video = result["entries"][0]
        url = f"https://www.youtube.com/watch?v={video['id']}"

        # Open the video in browser
        webbrowser.open(url)

        return f"Playing video: {url}"

    except Exception as e:
        return f"Error searching YouTube: {str(e)}"

#---------------------------------------------------

# ---------------- LLM SETUP ----------------
llm = AzureChatOpenAI(
    api_key=os.getenv("api_key"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("azure_endpoint"),   # e.g. https://xxx.openai.azure.com/
    azure_deployment="gpt-4o-mini", 
)
# -------------------------------------------   
agent_graph = create_agent(
    model=llm,
    tools=[write_file, run_python, list_files_with_query, modify_file, play_top_youtube_video],
    system_prompt="You are a local AI Coding Assistant running directly on the user's machine. You have access to tools that let you read, write, and execute code files. Use these tools to help the user with their coding tasks efficiently and accurately. Always think step-by-step and use the tools when needed.",
)

messa = input("How can Python Assitant Help You Today? ")
for step in agent_graph.stream(
    {"messages": [{"role": "user", "content": messa}]}
):
    for update in step.values():
        for message in update.get("messages", []):
            message.pretty_print()
