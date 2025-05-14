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
api_key = get_env_var("LLM_API_KEY") or "no-llm-api-key-provided"

model = OpenAIModel(llm, base_url=base_url, api_key=api_key)
embedding_model = get_env_var("EMBEDDING_MODEL") or "text-embedding-3-small"

logfire.configure(token=get_env_var("LOGFIRE_API_KEY"))
logfire.instrument_openai()

module_agent_prompt = """
# Role and Objective
Act as an API documentation architect. Your goal is to produce a comprehensive markdown summary of all entities in the Clinia API, highlighting their definitions, main attributes, and interconnections.

# Instructions
You can use the tool
- retrieve_relevant_documentation_tool and provide a user query to get relevant documentation from a vector database.
- For each entity, extract its definition, main attributes, and all explicit relationships to other entities (e.g., foreign keys, references, parent-child).

## Additional Instructions
- Ensure each entity section includes: name, description, main attributes, and relationships.
- Use clear headings and bullet points where appropriate.
- Ensure that each relationship is bidirectionally described where applicable.

# Reasoning Steps
1. Retrieve a list of entities from the API documentation.
2. For each entity, summarize its definition and main attributes.
3. Identify and list explicit relationships to other entities.
4. Format the output as markdown.

# Output Format
# Entity: <Entity Name>
## Description
<Description>
## Attributes
- <attribute_1>
- <attribute_2>
## Relationships
- <Relationship description with [[Related Entity]]>

# Examples
## Example 1

# Entity: Appointment
## Description
A scheduled meeting between a patient and a practitioner.
## Attributes
- id
- patient_id
- practitioner_id
- time
## Relationships
- References [[Patient]] (via patient_id)
- References [[Practitioner]] (via practitioner_id)

# Entity: Patient
## Description
An individual who receives medical care.
## Attributes
- id
- name
## Relationships
- Has many [[Appointment]]

# Context
You have access to a vector database containing the Clinia API documentation.

# Final instructions and prompt to think step by step
Proceed step by step: identify entities, summarize, extract attributes, relate, and format as markdown.
"""


@dataclass
class CliniaModuleAgentDeps:
    """
    Data class holding dependencies for the Clinia module agent.

    Attributes:
        supabase (Client): The Supabase client for database access.
        embedding_client (AsyncOpenAI): The OpenAI client for embedding generation.
    """
    supabase: Client
    embedding_client: AsyncOpenAI


tools_refiner_agent = Agent(model, system_prompt=module_agent_prompt, deps_type=CliniaModuleAgentDeps, retries=2)


@tools_refiner_agent.tool
async def retrieve_relevant_documentation(ctx: RunContext[CliniaModuleAgentDeps], query: str) -> str:
    """
    Tool to retrieve relevant documentation chunks for a given query using the agent's dependencies.

    Args:
        ctx (RunContext[CliniaModuleAgentDeps]): The agent's context containing dependencies.
        query (str): The user query string.

    Returns:
        str: Formatted documentation chunks or an error message if retrieval fails.
    """
    return await retrieve_relevant_documentation_tool(ctx.deps.supabase, ctx.deps.embedding_client, query)


async def main():
    """
    Main function to run the agent for extracting and saving Clinia API entities documentation.

    This function initializes the required clients and dependencies, runs the agent with a sample query,
    and saves the agent's response as a markdown file.
    """
    embedding_client, supabase = get_clients()

    deps = CliniaModuleAgentDeps(
        supabase=supabase,
        embedding_client=embedding_client,
    )

    query = "generate the markdown file containing the different entities from the clinia api documentation"
    response = await tools_refiner_agent.run(query, deps=deps)

    create_markdown_file("entities", response.data)

    print("Réponse de l'agent:")
    print(response.data)


if __name__ == "__main__":
    asyncio.run(main())
