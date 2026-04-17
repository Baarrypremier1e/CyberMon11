# 🛡️ CYBERMON v11 — Sentinel Protocol

Cybermon est une plateforme de simulation SIEM qui génère du trafic réseau réaliste pour entraîner les analystes SOC à détecter des patterns d'attaques (Brute Force, SQL Injection, DDoS) basés sur un modèle temporel circadien 

## Les Technologies
Backend : Python (FastAPI), PostgreSQL, Redis, websocket (pour temps reel).
Frontend : React, TypeScript, Tailwind CSS.
Infrastructure : Docker, Docker Compose
## Les fonctionnalités
Horloge accélérée : Simulez 24h de trafic en 24 minutes.
Modèle de Risque : Score dynamique basé sur la provenance (GeoIP) et l'heure.
Dashboard temps réel : Visualisation des alertes et scores critiques
Gestion des utilisateurs par l'administrateur

##  Installation & Lancement

### 1. Prérequis
* **Docker Desktop** installé et lancé.
* **Node.js** installé (pour le frontend).
* **PosgresSql** installé

### 2. Lancement de l'Infrastructure (Base de données & API)
```bash
cd backend
# Nettoyage et lancement des services Docker
docker compose down -v
docker compose up --build -d #assurer vous que le port 5432 et 8000 sont libre


cd ../frontend
npm install
npm run dev 
h+enter
o+enter

#l'application cybermon est ouverte dans votre navigateur 
#utiliser  azizarfaoui678@gmail.com/AzizArfa1234@@ pour se connecter comme admin
# Ou creer votre compte pour se connecter comme user

#entrer dans settings puis passer a 'simulation engine' cliquer sur 'run simulation' naviguer les differents  elements pour observer
```
### 3. Commande docker
```bash
docker compose up -d	#Lancer en arrière-plan
docker compose logs -f backend	#Voir les logs du moteur
docker compose down -v	#Arrêter et réinitialiser la base de données
```
### 4 acces a la base de données
```bash
docker exec -it cybermon_postgres psql -U cybermon -d cybermon # etant dans le repertoire backend

#Exemple : Voir les attaques par pays
SELECT country, COUNT(*) FROM events GROUP BY country ORDER BY 2 DESC; 
\dt #pour voir les tables 