import subprocess
from langchain.agents import create_agent
from langchain_openai import AzureChatOpenAI
# from langchain.tools import Tool
from langchain_core.tools import tool
import subprocess
import yt_dlp
import webbrowser
from dotenv import load_dotenv
import os

load_dotenv() 



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
def play_youtube_first(query: str) -> str:
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
    tools=[write_file, run_python,play_youtube_first]
)



messa = input("Write what python code you want to create and execute: ")
for step in agent_graph.stream(
    {"messages": [{"role": "user", "content": messa}]}
):
    for update in step.values():
        for message in update.get("messages", []):
            message.pretty_print()