FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source organisé
COPY src/ ./src/
COPY scripts/ ./scripts/

# Créer un volume pour le fichier .env
VOLUME /app/config

# Variable d'environnement pour pointer vers le fichier .env
ENV ENV_FILE=/app/config/.env

# Ajouter src/ au PYTHONPATH pour que les imports fonctionnent
ENV PYTHONPATH=/app

# Commande par défaut (peut être surchargée)
CMD ["python", "src/main.py"]
