"""
English Quest - Plataforma para aprender inglés jugando
=======================================================
- Login único: la profe entra con usuario y contraseña; el alumno con su usuario y PIN.
- Panel de la profe: temas, lecciones, alumnos, juegos rápidos y progreso.
- Panel del alumno: personita, mapa de lecciones y clase rápida en vivo.

Librerías usadas:
  - Flask            -> servidor web, páginas y sesiones
  - Flask-SocketIO   -> clase rápida en tiempo real
  - simple-websocket -> transporte WebSocket para Flask-SocketIO
  - PyMySQL          -> conexión con MySQL (Laragon)
  - segno            -> códigos QR
  - Werkzeug         -> encripta las contraseñas (viene con Flask)
  - Gunicorn         -> servidor de producción (solo en el hosting, Railway)

Ejecutar en tu compu:  python app.py
En Railway arranca solo con el Procfile (gunicorn).
"""
import sys
import time

from flask import Flask, session
from pymysql.err import OperationalError

import config
import db
import live  # noqa: F401  (registra los eventos de la clase rápida)
from auth import bp as auth_bp
from common import ACTIVITIES, SCENES, custom_scenes, public_base_url, socketio
from student import bp as student_bp
from teacher import bp as teacher_bp

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # imágenes de escenarios: hasta 8 MB por envío
app.register_blueprint(auth_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(student_bp)
socketio.init_app(app)


@app.context_processor
def globals_for_templates():
    # Los escenarios propios de la profe (para ella y para sus alumnos) se agregan a los de siempre
    custom = custom_scenes(session.get("teacher_id")) if session.get("role") else {}
    return {"ACTIVITIES": ACTIVITIES, "SCENES": {**SCENES, **custom}, "CUSTOM_SCENES": custom}


def prepare_database(tries=1):
    """Crea la base y las tablas. En el hosting reintenta, por si MySQL tarda en arrancar."""
    for attempt in range(1, tries + 1):
        try:
            db.init_db()
            return
        except OperationalError as e:
            if attempt == tries:
                print("\n❌ No me pude conectar a MySQL.")
                print("   En tu compu: ¿está encendido Laragon (botón 'Iniciar todo')?")
                print("   Si tu MySQL tiene contraseña, ponela en config.py (DB_PASSWORD).")
                print("   En Railway: revisá la variable MYSQL_URL del servicio.")
                print(f"   Detalle: {e}\n")
                sys.exit(1)
            print(f"⏳ MySQL todavía no responde, reintento {attempt}/{tries}…")
            time.sleep(3)


if __name__ != "__main__":
    # Lo está arrancando Gunicorn (Railway): preparar la base al cargar
    prepare_database(tries=10)


if __name__ == "__main__":
    prepare_database()

    print("\n" + "=" * 62)
    print("  🌟 ENGLISH QUEST está funcionando 🌟")
    print(f"  Base de datos: MySQL '{config.DB_NAME}' en {config.DB_HOST}:{config.DB_PORT}")
    print(f"  En esta compu:           http://localhost:{config.PORT}")
    print(f"  Desde celulares (Wi-Fi): {public_base_url()}")
    print("  (Los celulares tienen que estar en la MISMA red Wi-Fi)")
    print("=" * 62 + "\n")
    socketio.run(app, host="0.0.0.0", port=config.PORT, debug=False, allow_unsafe_werkzeug=True)
