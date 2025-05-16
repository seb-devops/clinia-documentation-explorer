# Clinia Documentation explorer
Personal project to facilitate the exploration of Clinia's documentation 
using a rag and a Agent that can query it.

The project use:

- Supabase for the vector database
- PydanticAI for the agent
- A jupyter notebook with sample data for evals
- logfire for monitoring the agent
- Streamlit for the web interface

## Setup
1. Install the dependencies:

```bash
uv sync --dev
```

2. Enter the virtual environment:

```bash
source .venv/bin/activate or .venv\Scripts\activate(Windows)
```

3. Create a `.env` file in the root directory and add your environment variables. You can use the provided `.env.example` as a template.


## Usage

### Supabase

Create your Supabase project and then run the script
`supabase_script/initialisation.sql` in the sql editor 
to create the table, the stored procedures, basic security rule and the index.

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

This will run the agent, and ask a sample question which you can modify in the main function of the file `src/clinia-doc-agent.py`.

The agent can now be queried via the Streamlit web interface, in addition to the command line usage.

### Evals
To run the evals, run all the cells in the file `src/clinia-doc-evals.ipynb`. This will run the evals for testing the agent. It will append to a csv file the results of the evals. This contains:

- The execution time of the agent
- The number of token used by the agent
- The accuracy of the answer generate by comparing to an expected answer

The purpose of the evals folder is to generate a dataset to evaluate the performance of the agent while iterating on it.

## Web Interface (Streamlit)

A simple web interface using Streamlit is now available to interact with the agent.

### Launch the interface locally

Make sure you have a `.env` file at the root of the project (see `.env.example`).

```bash
streamlit run src/clinia_streamlit_app.py
```

Then open http://localhost:8501 in your browser.

### Launch the interface via Docker (local)

To use your local `.env` file with Docker:

```bash
docker build -t clinia-doc-app .
docker run --env-file .env -p 8000:8000 clinia-doc-app
```

Open http://localhost:8000 in your browser.

## Project version 

### Version 1
 - Crawler to extract documentation from the Clinia website and store it in supabase
 - Agent to ask simple questions to the documentation
 - Use logfire to monitor the agent( Compatible with OpenTelemetry)
 - Initial evals to test if the agent can answer the questions correctly.

### Version 2 ( TODO)
 - Adding more robust evaluation that test the whole answer and not only some keywords
 - Adding guardrails to the agent to avoid unexpected behavior
 - Add unit tests to validate tools and crawler
 - Improve metadata on the chunks to filter the results before embedding and improve the performance of the agent


### Version 3 ( TODO)
 - Put the retriever behind an api to secure the access to the vector database
 - Add a web interface to ask questions to the agent
 - Answer complex query by using agentic RAG
 - Improve monitoring to be able to follow accurately the behavior of the agents
