import requests
import time
import threading
import random

SERVER_URL = "https://hybrid-miner-server.onrender.com"  # замени на свой URL Render
USERNAME = input("Введите имя пользователя: ")

# Регистрация пользователя
try:
    r = requests.post(f"{SERVER_URL}/register?username={USERNAME}")
    try:
        data = r.json()
    except ValueError:
        data = {"status": "error", "message": "Пустой или невалидный JSON"}
    print("Регистрация:", data)
except requests.exceptions.RequestException as e:
    print("Ошибка регистрации:", e)

# Функция для отправки хэшрейта
def send_hashrate(hashrate):
    try:
        r = requests.post(f"{SERVER_URL}/send_hashrate", json={"username": USERNAME, "hashrate": hashrate}, timeout=10)
        try:
            data = r.json()
        except ValueError:
            data = {"status": "error", "message": "Пустой или невалидный JSON"}
        print(f"Отправка хэшрейта {hashrate}: {data}")
    except requests.exceptions.RequestException as e:
        print("Ошибка отправки хэшрейта:", e)

# Функция для получения баланса
def get_balance():
    try:
        r = requests.get(f"{SERVER_URL}/get_balance/{USERNAME}", timeout=10)
        try:
            data = r.json()
            balance = data.get("balance", 0)
            print(f"Баланс: {balance:.4f}")
        except ValueError:
            print("Ошибка получения баланса: пустой или невалидный JSON")
    except requests.exceptions.RequestException as e:
        print("Ошибка получения баланса:", e)

# Функция для симуляции хэшрейта (позже можно заменить на реальный сбор)
def simulate_hashrate():
    return round(random.uniform(1.0, 10.0), 2)  # случайное значение между 1 и 10

# Интервал автоотправки хэшрейта
INTERVAL = 10  # секунд

# Функция автоотправки
def auto_send():
    while True:
        hr = simulate_hashrate()
        send_hashrate(hr)
        get_balance()
        time.sleep(INTERVAL)

# Запуск в отдельном потоке
thread = threading.Thread(target=auto_send, daemon=True)
thread.start()

print("Автоотправка хэшрейта запущена. Ctrl+C для остановки.")

# Держим основной поток активным
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nКлиент остановлен пользователем.")
