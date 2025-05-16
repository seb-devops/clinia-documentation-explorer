FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

COPY . .

RUN uv sync --locked

EXPOSE 8000

CMD ["uv", "run", "streamlit", "run", "clinia_streamlit_app.py", "--server.port=8000", "--server.address=0.0.0.0"]
 