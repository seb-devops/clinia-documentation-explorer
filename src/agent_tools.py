import os
import sys
from typing import List

from openai import AsyncOpenAI
from supabase import Client

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_env_var

embedding_model = get_env_var("EMBEDDING_MODEL") or "text-embedding-3-small"


async def get_embedding(text: str, embedding_client: AsyncOpenAI) -> List[float]:
    """Get embedding vector from OpenAI."""
    try:
        response = await embedding_client.embeddings.create(model=embedding_model, input=text)
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return [0] * 1536  # Return zero vector on error


async def retrieve_relevant_documentation_tool(supabase: Client, embedding_client: AsyncOpenAI, user_query: str) -> str:
    try:
        # Get the embedding for the query
        query_embedding = await get_embedding(user_query, embedding_client)

        # Query Supabase for relevant documents
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
