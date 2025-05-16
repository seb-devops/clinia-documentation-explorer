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
### Launch the interface locally
Run the following command to start the Streamlit app:

```bash
streamlit run src/clinia_streamlit_app.py
```

Then open http://localhost:8501 in your browser.

### Evals
To run the evals, run all the cells in the file `src/clinia-doc-evals.ipynb`. This will run the evals for testing the agent. It will append to a csv file the results of the evals. This contains:

- The execution time of the agent
- The accuracy of the answer generate by comparing to an expected answer

The purpose of the evals folder is to generate a dataset to evaluate the performance of the agent while iterating on it.

### Launch the interface via Docker (local)

To use your local `.env` file with Docker:

```bash
docker build -t clinia-doc-app .
docker run --env-file .env -p 8000:8000 clinia-doc-app
```

Open http://localhost:8000 in your browser.

## Features and Roadmap

### Current Features
 - Crawler to extract documentation from the Clinia website and store it in supabase
 - Agent to ask simple questions to the documentation
 - Use logfire to monitor the agent( Compatible with OpenTelemetry)
 - Initial evals to test if the agent can answer the questions correctly.

### New features
 - Add complex queries that requires multiple steps to answer

### RAG improvements
 - Add a reranker model to improve the results of the retriever
 - Improve metadata on the chunks to filter the results before embedding and improve the performance of the agent

### Evaluations and test improvements
 - Evaluate RAG accuracy and use LLM-as-a-judge to validate the results
 - Add unit tests to validate tools and crawler

### Deployment and monitoring improvements
 - Add ci/cd to deploy the agent and the crawler

### Road to production improvement
 - Put the agent in a api to get more control(Authentication, rate limiting, etc.)
 - Custom chatbot to interact with the agent in react
 - Adding guardrails to the agent to avoid unexpected behavior


