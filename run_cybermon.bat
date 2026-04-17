@echo off
echo 🚀 Démarrage de CYBERMON - Sentinel Protocol...

echo 📦 Nettoyage et lancement Docker...
docker compose down -v
docker compose up --build -d

echo ⏳ Attente du démarrage des services...
timeout /t 5

echo 🌐 Lancement du Frontend...
cd frontend
call npm install
npm run dev -- --open