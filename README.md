# Clinia Documentation explorer
Personal project to facilitate the exploration of Clinia's documentation 
using a rag and a Agent that can query it.

The project use:

- supabase for the vector database
- PydancticAI for the agent 
- A jupyter notebook with sample data for evals
- logfire for monitoring the agent

## Setup
1. Install the dependenciees: 

```bash
uv sync --dev
```

2. Enter the virtual environment:

```bash
source .venv/bin/activate or .venv\Scripts\activate(Windows)
```

3. Create a `.env` file in the root directory and add your environment variables. You can use the provided `.env.example` as a template.


## Usage

### Crawler
To run the crawler, use the following command:

```bash
python src/clinia-doc-crawler.py
```
This will extract documentation from the Clinia website and store it in Supabase.
### Agent
To run the agent, use the following command:

```bash
python src/clinia-doc-agent.py
```

This will run the agent, which will extract entities and relationships from the API documentation and create a markdown file with the results.

### Evals
To run the evals, run all the cells in the file `src/clinia-doc-evals.ipynb`. This will run the evals for testing the agent. It will append to a csv file the results of the evals. This contains:

- The execution time of the agent
- The number of token used by the agent
- The accuracy of the answer generate by comparing to an expected answer

The purpose of the evals folder is to generate a dataset to evaluate the performance of the agent while iterating on it.

## Project version 

### Version 1
 - Crawler to extract documentation from the Clinia website and store it in supabase
 - Agent to ask simple questions to the documentation
 - Use logfire to monitor the agent( Compatible with OpenTelemetry)
 - Initial evals to test if the agent can answer the questions correctly.

### Version 2 ( TODO)
 - Adding evals question for testing the agent with pydanticAI evals module
 - Add unit tests to validate tools and crawler
 - Improve metadata on the chunks to filter the results before embedding

### Version 3 ( TODO)
 - Answer complex query by using agentic RAG
 - Improve Monitoring to be able to follow accurately the behavior of the agents
