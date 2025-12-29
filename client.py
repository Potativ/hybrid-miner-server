from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import sqlite3
import os

app = FastAPI(title="Hybrid Miner Server")

DB_PATH = "database.db"

# Инициализация базы данных при первом запуске
if not os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE hashrates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            hashrate REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE balance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def db_execute(query, params=()):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def db_query(query, params=()):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.close()
    return result

class Hashrate(BaseModel):
    username: str
    hashrate: float

@app.post("/register")
def register(username: str):
    try:
        db_execute("INSERT INTO users (username) VALUES (?)", (username,))
        user_id = db_query("SELECT id FROM users WHERE username=?", (username,))[0][0]
        db_execute("INSERT INTO balance (user_id, amount) VALUES (?, 0)", (user_id,))
        return JSONResponse(content={"status": "ok"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"status": "exists", "message": str(e)}, status_code=200)

@app.post("/send_hashrate")
def send_hashrate(data: Hashrate):
    try:
        user = db_query("SELECT id FROM users WHERE username=?", (data.username,))
        if not user:
            return JSONResponse(content={"status": "error", "message": "User not found"}, status_code=200)
        user_id = user[0][0]
        db_execute("INSERT INTO hashrates (user_id, hashrate) VALUES (?, ?)", (user_id, data.hashrate))
        db_execute("UPDATE balance SET amount = amount + ? WHERE user_id=?", (data.hashrate * 0.01, user_id))
        return JSONResponse(content={"status": "ok"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

@app.get("/get_balance/{username}")
def get_balance(username: str):
    try:
        user = db_query("SELECT id FROM users WHERE username=?", (username,))
        if not user:
            return JSONResponse(content={"status": "error", "message": "User not found"}, status_code=200)
        user_id = user[0][0]
        bal = db_query("SELECT amount FROM balance WHERE user_id=?", (user_id,))
        return JSONResponse(content={"status": "ok", "balance": bal[0][0]}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)
