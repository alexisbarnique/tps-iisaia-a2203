#!/usr/bin/env python3
import sys
from pathlib import Path
import httpx

BASE_URL = "http://localhost:8000/api"
TOKEN_FILE = Path.home() / ".config" / "lifetracker" / "token"

def get_token():
    return TOKEN_FILE.read_text().strip() if TOKEN_FILE.exists() else None

def save_token(token):
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(token)

def authenticate():
    print("No hay sesión guardada. Iniciá sesión:")
    email = input("Email: ").strip()
    password = input("Contraseña: ").strip()
    res = httpx.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if res.status_code != 200:
        print(f"Error: {res.json().get('detail', 'credenciales inválidas')}")
        sys.exit(1)
    token = res.json()["access_token"]
    save_token(token)
    print("✓ Sesión iniciada")
    return token

def prompt_entry():
    print("\n¿Qué querés registrar?")
    print("  1. Evento / Concierto")
    print("  2. Película / Serie")
    print("  3. Libro")
    print("  4. Ciudad")
    print("  5. Lugar (restaurante, museo…)")
    choice = input("\nOpción (1-5): ").strip()
    categories = {"1": "event", "2": "movie_series", "3": "book", "4": "city", "5": "place"}
    if choice not in categories:
        print("Opción inválida"); sys.exit(1)
    category = categories[choice]

    title = input("Nombre/Título: ").strip()
    date = input("Fecha (YYYY-MM-DD): ").strip()
    notes = input("Notas (Enter para saltar): ").strip() or None

    entry = {"category": category, "title": title, "date": date}
    if notes:
        entry["notes"] = notes

    if category == "movie_series":
        saga = input("Saga (Enter para saltar): ").strip()
        if saga:
            entry["saga_name"] = saga
            part = input("Número de entrega: ").strip()
            if part.isdigit():
                entry["saga_part"] = int(part)
        season = input("Temporada (Enter para saltar): ").strip()
        if season.isdigit():
            entry["season_number"] = int(season)
        rating = input("Calificación 1-5 (Enter para saltar): ").strip()
        if rating.isdigit() and 1 <= int(rating) <= 5:
            entry["rating"] = int(rating)

    elif category == "book":
        saga = input("Saga (Enter para saltar): ").strip()
        if saga:
            entry["saga_name"] = saga
            part = input("Número de entrega: ").strip()
            if part.isdigit():
                entry["saga_part"] = int(part)
        rating = input("Calificación 1-5 (Enter para saltar): ").strip()
        if rating.isdigit() and 1 <= int(rating) <= 5:
            entry["rating"] = int(rating)

    elif category == "city":
        country = input("País (Enter para saltar): ").strip()
        if country:
            entry["country"] = country

    elif category == "place":
        print("Tipo: restaurant / cafe / museum / bar / park / other")
        place_type = input("Tipo: ").strip()
        if place_type:
            entry["place_type"] = place_type
        city = input("Ciudad (Enter para saltar): ").strip()
        if city:
            entry["city"] = city
        country = input("País (Enter para saltar): ").strip()
        if country:
            entry["country"] = country
        rating = input("Calificación 1-5 (Enter para saltar): ").strip()
        if rating.isdigit() and 1 <= int(rating) <= 5:
            entry["rating"] = int(rating)

    return entry

def post_entry(entry, token):
    headers = {"Authorization": f"Bearer {token}"}
    res = httpx.post(f"{BASE_URL}/entries", json=entry, headers=headers)
    return res

def main():
    token = get_token() or authenticate()
    entry = prompt_entry()
    res = post_entry(entry, token)

    if res.status_code == 401:
        print("Sesión expirada, reautenticando…")
        token = authenticate()
        res = post_entry(entry, token)

    if res.status_code == 201:
        data = res.json()
        saga_info = f" — {data['saga_name']} #{data['saga_part']}" if data.get("saga_name") else ""
        print(f"\n✓ Registrado: '{data['title']}' [{data['category']}]{saga_info}")
    else:
        print(f"Error {res.status_code}: {res.json()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
