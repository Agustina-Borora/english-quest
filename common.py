"""
Cosas compartidas: el objeto socketio, los "decoradores" que protegen las páginas
(solo profe / solo alumno) y funciones de ayuda.
"""
import json
import random
import re
import socket
import unicodedata
from functools import wraps

from flask import redirect, request, session, url_for
from flask_socketio import SocketIO

import config
import db

socketio = SocketIO(async_mode="threading", cors_allowed_origins="*")

ACTIVITIES = {
    "explore": {"emoji": "🔍", "name": "Explorar", "desc": "Tocar los objetos de la escena para aprender cada palabra"},
    "cards": {"emoji": "🃏", "name": "Tarjetas", "desc": "Tarjetas que se dan vuelta: palabra, dibujo y traducción"},
    "read": {"emoji": "👂", "name": "Leer y escuchar", "desc": "Leer o escuchar la palabra y elegir la correcta"},
    "write": {"emoji": "✍️", "name": "Escribir", "desc": "Armar la palabra letra por letra"},
    "quiz": {"emoji": "🏁", "name": "Desafío final", "desc": "Preguntas de traducción para cerrar la lección"},
}

SCENES = {
    "house": {"name": "House", "es": "Casa"},
    "supermarket": {"name": "Supermarket", "es": "Supermercado"},
    "school": {"name": "School", "es": "Escuela"},
    "park": {"name": "Park", "es": "Parque"},
    "zoo": {"name": "Zoo", "es": "Zoológico"},
    "beach": {"name": "Beach", "es": "Playa"},
}

DEFAULT_AVATAR = {"skin": 1, "hair": 0, "hairColor": 0, "eyes": 0, "top": 0, "topColor": 1,
                  "pants": 0, "accessory": 0}


# ------------------------------------------------------------ protección de páginas
def teacher_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if session.get("role") != "teacher":
            return redirect(url_for("auth.login", next=request.full_path))
        return view(*args, **kwargs)
    return wrapper


def student_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if session.get("role") != "student":
            return redirect(url_for("auth.login", next=request.full_path))
        return view(*args, **kwargs)
    return wrapper


def current_teacher_id():
    return session.get("teacher_id") if session.get("role") == "teacher" else None


def current_student_id():
    return session.get("student_id") if session.get("role") == "student" else None


# ------------------------------------------------------------ ayudas
def safe_int(value, default=0, low=None, high=None):
    try:
        n = int(value)
    except (TypeError, ValueError):
        return default
    if low is not None:
        n = max(low, n)
    if high is not None:
        n = min(high, n)
    return n


def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", text.lower())


def username_taken(username):
    return bool(db.query_one("SELECT id FROM teachers WHERE username=%s", (username,)) or
                db.query_one("SELECT id FROM students WHERE username=%s", (username,)))


def make_student_username(name):
    """Usuario fácil para chicos: primer nombre + 2 números (ej: sofia27)."""
    base = slugify(name.split()[0] if name.split() else "alumno")[:12] or "alumno"
    for _ in range(200):
        candidate = f"{base}{random.randint(10, 99)}"
        if not username_taken(candidate):
            return candidate
    return f"{base}{random.randint(100, 9999)}"


def make_pin():
    return f"{random.randint(0, 9999):04d}"


def parse_avatar(raw):
    try:
        data = json.loads(raw) if raw else {}
    except (TypeError, ValueError):
        data = {}
    avatar = dict(DEFAULT_AVATAR)
    for key in DEFAULT_AVATAR:
        if key in data:
            avatar[key] = safe_int(data[key], DEFAULT_AVATAR[key], 0, 20)
    return avatar


def get_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def public_base_url():
    if config.PUBLIC_URL:
        return config.PUBLIC_URL.rstrip("/")
    return f"http://{get_lan_ip()}:{config.PORT}"


def lesson_words(lesson_id):
    return db.query(
        "SELECT w.word, w.translation, w.emoji, w.sentence FROM words w "
        "JOIN lesson_topics lt ON lt.topic_id = w.topic_id WHERE lt.lesson_id=%s "
        "ORDER BY w.topic_id, w.position, w.id", (lesson_id,))


def lesson_activities(lesson):
    return [a for a in lesson["activities"].split(",") if a in ACTIVITIES]
