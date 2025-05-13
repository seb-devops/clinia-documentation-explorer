# Clinia Documentation explorer
Personal project to facilitate the exploration of Clinia's documentation using a rag and a Agent that can query it.

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
 - Agent to extract entities and relationships from the api documentation
 - Use logfire to monitor the agent
 
 The agent create a markdown file with every entities and their relationships.

### Version 2
 - Adding evals for testing the agent
 - Adding a second agent that validate each entity and relationship with the markdown file

### Version 3

