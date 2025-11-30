import subprocess
from langchain.agents import create_agent
from langchain_openai import AzureChatOpenAI
# from langchain.tools import Tool
from langchain_core.tools import tool
import subprocess
from typing import List
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
def summarize_files(file_list: str) -> str:
    """
    Summarize the content of the given files.
    Input: A comma-separated string of filenames (e.g. "a.txt,b.md,c.py").
    Output: A text summary of all file contents.
    """

    try:
        # Convert comma-separated input into a clean list
        files = [f.strip() for f in file_list.split(",") if f.strip()]
        if not files:
            return "No valid files provided."

        summaries = []

        for filename in files:
            if not os.path.exists(filename):
                summaries.append(f"❌ File not found: {filename}")
                continue

            if not os.path.isfile(filename):
                summaries.append(f"⚠️ Not a file: {filename}")
                continue

            try:
                with open(filename, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Simple summarization logic (replace this with LLM if desired)
                summary = content[:400] + "..." if len(content) > 400 else content

                summaries.append(f"### Summary of {filename}:\n{summary}\n")

            except Exception as e:
                summaries.append(f"Error reading {filename}: {str(e)}")

        return "\n".join(summaries)

    except Exception as e:
        return f"Error: {str(e)}"




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
    tools=[write_file, run_python,play_youtube_first,list_files_with_query,summarize_files]
)



messa = input("Write what python code you want to create and execute: ")
for step in agent_graph.stream(
    {"messages": [{"role": "user", "content": messa}]}
):
    for update in step.values():
        for message in update.get("messages", []):
            message.pretty_print()