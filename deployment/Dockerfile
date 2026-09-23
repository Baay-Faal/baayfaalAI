# Dockerfile souverain ultra-épuré pour l'Agent Baay-Faal (< 80 Mo)
FROM python:3.11-slim

LABEL maintainer="Baay-Faal Engineering Team"
LABEL description="Agent IA Local Autonome & Souverain 100% Vanilla Python"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Copie de l'intégralité du projet (Vanilla First : zéro pip install)
COPY . /app/

# Port pour le démon de nœud distant si activé
EXPOSE 9999

# Point d'entrée principal
ENTRYPOINT ["python", "main.py"]
