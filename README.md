# Hybrid Miner Server (MVP)

Backend API for a voluntary hybrid mining application.

## Endpoints
- POST /register?username=NAME
- POST /send_hashrate { username, hashrate }
- GET /get_balance/{username}

## Run locally
pip install -r requirements.txt
uvicorn main:app --reload

## Deploy on Render
Start command:
uvicorn main:app --host 0.0.0.0 --port 10000
