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
        "SELECT w.topic_id, w.word, w.translation, w.emoji, w.sentence FROM words w "
        "JOIN lesson_topics lt ON lt.topic_id = w.topic_id WHERE lt.lesson_id=%s "
        "ORDER BY lt.position, w.topic_id, w.position, w.id", (lesson_id,))


def lesson_activities(lesson):
    return [a for a in lesson["activities"].split(",") if a in ACTIVITIES]


def lesson_topic_rows(lesson_id):
    """Los temas de una lección, en el orden que eligió la profe, con su escenario y actividades."""
    return db.query("SELECT lt.topic_id, lt.position, lt.scene, lt.activities, t.title, t.emoji FROM lesson_topics lt "
                    "JOIN topics t ON t.id=lt.topic_id WHERE lt.lesson_id=%s ORDER BY lt.position, t.id",
                    (lesson_id,))


def lesson_steps(lesson, topic_rows=None):
    """
    Los pasos (actividades) de una lección, en orden.
    - Todos los temas juntos: un paso por actividad, con todas las palabras mezcladas (clave = actividad).
    - Cada tema por separado: los pasos de cada tema, con su escenario (clave = "idTema-actividad").
    """
    if not lesson.get("by_topic"):
        return [{"key": a, "activity": a, "topic_id": None, "scene": lesson["scene"]} for a in lesson_activities(lesson)]
    rows = topic_rows if topic_rows is not None else lesson_topic_rows(lesson["id"])
    steps = []
    for t in rows:
        for a in t["activities"].split(","):
            if a in ACTIVITIES:
                steps.append({"key": f"{t['topic_id']}-{a}", "activity": a, "topic_id": t["topic_id"],
                              "topic": t["title"], "topic_emoji": t["emoji"], "scene": t["scene"] or lesson["scene"]})
    return steps


def lesson_step_keys(lesson):
    return [s["key"] for s in lesson_steps(lesson)]


# ------------------------------------------------------------ escenarios propios (con imagen)
def custom_scenes(teacher_id):
    """Escenarios que creó la profe con sus imágenes. La clave es "c" + id (ej: c7)."""
    if not teacher_id:
        return {}
    rows = db.query("SELECT id, name, slots FROM custom_scenes WHERE teacher_id=%s ORDER BY id", (teacher_id,))
    return {f"c{r['id']}": {"name": r["name"], "es": r["name"], "custom": True,
                            "img": url_for("auth.scene_image", scene_id=r["id"]), "slots": parse_slots(r["slots"])}
            for r in rows}


def all_scenes(teacher_id):
    return {**SCENES, **custom_scenes(teacher_id)}


def parse_slots(raw):
    """
    Lugares (en %) donde aparecen las palabras sobre la imagen: [[x, y, "nombre"], ...].
    El nombre (ej: "cabeza") es opcional: si coincide con una palabra o su traducción, esa palabra va ahí.
    """
    try:
        data = json.loads(raw) if raw else []
    except (TypeError, ValueError):
        return []
    out = []
    for p in data if isinstance(data, list) else []:
        if isinstance(p, (list, tuple)) and len(p) in (2, 3):
            label = str(p[2]).strip()[:40] if len(p) == 3 and p[2] is not None else ""
            out.append([safe_int(p[0], 50, 3, 97), safe_int(p[1], 50, 5, 95), label])
    return out[:12]
