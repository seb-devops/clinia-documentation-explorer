from __future__ import annotations as _annotations

import asyncio
import os
import sys
from dataclasses import dataclass

import logfire
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIModel
from supabase import Client

from agent_tools import retrieve_relevant_documentation_tool
from utils import create_markdown_file, get_clients, get_env_var

load_dotenv()

# Configuration des modèles
llm = get_env_var("PRIMARY_MODEL") or "gpt-4.1-mini"
base_url = get_env_var("BASE_URL") or "https://api.openai.com/v1"
api_key = get_env_var("OPENAI_API_KEY") or "no-llm-api-key-provided"

model = OpenAIModel(llm, base_url=base_url, api_key=api_key)
embedding_model = get_env_var("EMBEDDING_MODEL") or "text-embedding-3-small"

logfire.configure(token=get_env_var("LOGFIRE_API_KEY"))
logfire.instrument_openai()

clinia_docs_agent_prompt = """
# Role
You are a Clinia documentation expert. Your mission is to accurately answer any user question by locating and synthesizing the most relevant information in the Clinia documentation.

# Documentation structure
1. Guide – overviews, concepts, getting-started material.
2. Recipes – step-by-step tutorials and best practices.
3. API Reference – complete endpoint specifications.

# Available tool
- retrieve_relevant_documentation: fetches relevant documentation for a given query.

# Step-by-step reasoning

1. Find all references to the user query in the documentation.
2. Iterate multiple times with your tools to get all relevant information.
3. If you are not sure about the answer, use the retrieved information to create new query
4. when you are confident about the answer, format it in markdown and return it. 

Always think step by step and make sure to validate your answer
"""


@dataclass
class CliniaDocAgentsDeps:
    """
    Data class holding dependencies for the Clinia module agent.

    Attributes:
        supabase (Client): The Supabase client for database access.
        embedding_client (AsyncOpenAI): The OpenAI client for embedding generation.
    """

    supabase: Client
    embedding_client: AsyncOpenAI


clinia_docs_agent = Agent(model, system_prompt=clinia_docs_agent_prompt, deps_type=CliniaDocAgentsDeps, retries=2)


@clinia_docs_agent.tool
async def retrieve_relevant_documentation(ctx: RunContext[CliniaDocAgentsDeps], query: str) -> str:
    """
    Tool to retrieve relevant documentation chunks for a given query using the agent's dependencies.

    Args:
        ctx (RunContext[CliniaDocAgentsDeps]): The agent's context containing dependencies.
        query (str): The user query string.

    Returns:
        str: Formatted documentation chunks or an error message if retrieval fails.
    """
    with logfire.span("create embedding for {search_query=}", search_query=query):
        return await retrieve_relevant_documentation_tool(ctx.deps.supabase, ctx.deps.embedding_client, query)


async def main():
    """
    Main function to run the agent for extracting and saving Clinia API entities documentation.

    This function initializes the required clients and dependencies, runs the agent with a sample query,
    and saves the agent's response as a markdown file.
    """
    embedding_client, supabase = get_clients()

    deps = CliniaDocAgentsDeps(
        supabase=supabase,
        embedding_client=embedding_client,
    )

    query = "Through which mecanism a human can be part of the Resolution process ? "
    response = await clinia_docs_agent.run(query, deps=deps)

    create_markdown_file("modules", response.data)

    print("Réponse de l'agent:")
    print(response.data)


if __name__ == "__main__":
    asyncio.run(main())
