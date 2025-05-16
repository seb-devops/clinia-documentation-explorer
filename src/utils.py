import logging
import os
from typing import Optional

from dotenv import load_dotenv
from openai import AsyncOpenAI
from supabase import Client

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("clinia-doc-crawler")

load_dotenv()


def get_env_var(key: str) -> Optional[str]:
    value = os.getenv(key)
    if value is None:
        return None
    return bytes(value, "utf-8").decode("unicode_escape")


def get_clients():
    openai_client = None
    base_url = get_env_var("BASE_URL") or "https://api.openai.com/v1"
    api_key = get_env_var("OPENAI_API_KEY") or "no-api-key-provided"

    openai_client = AsyncOpenAI(base_url=base_url, api_key=api_key)  # Supabase client setup

    supabase = None

    supabase_url = f"https://{get_env_var("SUPABASE_URL")}"
    supabase_key = get_env_var("SUPABASE_SERVICE_KEY")

    if supabase_url and supabase_key:
        try:
            supabase: Client = Client(supabase_url, supabase_key)

        except Exception as e:
            log.error(f"Error initializing Supabase client: {e}")
            supabase = None
    return openai_client, supabase


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
