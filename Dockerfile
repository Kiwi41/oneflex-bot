FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY *.py .
COPY *.md .

# Créer un volume pour le fichier .env
VOLUME /app/config

# Variable d'environnement pour pointer vers le fichier .env
ENV ENV_FILE=/app/config/.env

# Commande par défaut (peut être surchargée)
CMD ["python", "main.py"]
