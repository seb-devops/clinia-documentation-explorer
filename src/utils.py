import json
import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from openai import AsyncOpenAI
from supabase import Client

# Directory where the workbench files are stored
workbench_dir = os.path.join(os.path.dirname(__file__), "..", "workbench")

load_dotenv()

def get_env_var(key: str) -> Optional[str]:
    value = os.getenv(key)
    if value is None:
        return None
    return bytes(value, "utf-8").decode("unicode_escape")



def get_clients():
    base_url = get_env_var("BASE_URL") or "https://api.openai.com/v1"
    api_key = get_env_var("LLM_API_KEY") or "no-api-key-provided"

    openai_client = AsyncOpenAI(base_url=base_url, api_key=api_key)  # Supabase client setup

    supabase_url = get_env_var("SUPABASE_URL")
    supabase_key = get_env_var("SUPABASE_KEY")

    if supabase_url and supabase_key:
        try:
            supabase: Client = Client(supabase_url, supabase_key)
        except Exception as e:
            print(f"Failed to initialize Supabase: {e}")
            write_to_log(f"Failed to initialize Supabase: {e}")

    return openai_client, supabase


def write_to_log(message: str):
    """Write a message to the logs.txt file in the workbench directory.

    Args:
        message: The message to log
    """
    # Get the directory one level up from the current file
    log_path = os.path.join(workbench_dir, "logs.txt")
    os.makedirs(workbench_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_entry)


def create_markdown_file(filename: str, content: str) -> str:
    """Create a markdown file at the project root with the given content.

    Args:
        filename: Name of the markdown file (without .md extension)
        content: Content to write in the markdown file

    Returns:
        str: The absolute path of the created file
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(project_root, f"{filename}.md")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return file_path
