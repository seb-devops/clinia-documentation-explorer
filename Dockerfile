# Dockerfile pour déployer une application Streamlit sur Azure App Service
# Suivant les best practices Azure (image officielle, port 8000, pas de credentials en dur)

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Copier le code source dans l'image
COPY . .

RUN uv sync --locked

# Exposer le port 8000 (requis par Azure App Service pour custom containers)
EXPOSE 8000

# Commande de lancement : Streamlit sur le port 8000
CMD ["uv", "run", "streamlit", "run", "clinia_streamlit_app.py", "--server.port=8000", "--server.address=0.0.0.0"]
 