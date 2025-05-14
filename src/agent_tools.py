import os
import sys
from typing import List

from openai import AsyncOpenAI
from supabase import Client

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_env_var

embedding_model = get_env_var("EMBEDDING_MODEL") or "text-embedding-3-small"


async def get_embedding(text: str, embedding_client: AsyncOpenAI) -> List[float]:
    """
    Asynchronously get the embedding vector for a given text using OpenAI.

    Args:
        text (str): The text to embed.
        embedding_client (AsyncOpenAI): The OpenAI client to use for embedding.

    Returns:
        List[float]: The embedding vector for the text, or a zero vector on error.
    """
    try:
        response = await embedding_client.embeddings.create(model=embedding_model, input=text)
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return [0] * 1536  # Return zero vector on error


async def retrieve_relevant_documentation_tool(supabase: Client, embedding_client: AsyncOpenAI, user_query: str) -> str:
    """
    Retrieve and format the most relevant documentation chunks for a user query using vector search.

    Args:
        supabase (Client): The Supabase client for database access.
        embedding_client (AsyncOpenAI): The OpenAI client for embedding generation.
        user_query (str): The user's query string.

    Returns:
        str: Formatted documentation chunks or an error message if retrieval fails.
    """
    try:
        query_embedding = await get_embedding(user_query, embedding_client)

        result = supabase.rpc(
            "match_site_pages",
            {"query_embedding": query_embedding, "match_count": 10, "filter": {"source": "pydantic_ai_docs"}},
        ).execute()

        if not result.data:
            return "No relevant documentation found."

        # Format the results
        formatted_chunks = []
        for doc in result.data:
            chunk_text = f"""
                # {doc["title"]}

                {doc["content"]}
            """
            formatted_chunks.append(chunk_text)

        # Join all chunks with a separator
        return "\n\n---\n\n".join(formatted_chunks)

    except Exception as e:
        print(f"Error retrieving documentation: {e}")
        return f"Error retrieving documentation: {str(e)}"
