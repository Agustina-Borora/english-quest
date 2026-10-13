"""
Configuración de English Quest.

EN TU COMPU (Laragon): usa MySQL con usuario "root" SIN contraseña, en localhost:3306.
Si tu MySQL tiene contraseña, cambiala acá abajo (DB_PASSWORD).

EN RAILWAY (hosting): no hace falta tocar este archivo. Los datos se leen solos de las
variables de entorno:
  - MYSQL_URL                 -> la conexión a la base MySQL de Railway
  - SECRET_KEY                -> clave secreta para las sesiones
  - RAILWAY_PUBLIC_DOMAIN     -> la dirección pública (la usa el QR); Railway la pone sola
  - PORT                      -> el puerto; Railway lo pone solo
"""
import os
from urllib.parse import unquote, urlparse

# ---------------------------------------------------------------- MySQL en tu compu
DB_HOST = os.environ.get("EQ_DB_HOST") or os.environ.get("MYSQLHOST") or "localhost"
DB_PORT = int(os.environ.get("EQ_DB_PORT") or os.environ.get("MYSQLPORT") or 3306)
DB_USER = os.environ.get("EQ_DB_USER") or os.environ.get("MYSQLUSER") or "root"
DB_PASSWORD = os.environ.get("EQ_DB_PASSWORD") or os.environ.get("MYSQLPASSWORD") or ""
DB_NAME = os.environ.get("EQ_DB_NAME") or os.environ.get("MYSQLDATABASE") or "english_quest"

# ---------------------------------------------------------------- MySQL en el hosting
# Si existe MYSQL_URL (formato mysql://usuario:clave@host:puerto/base), tiene prioridad.
_url = os.environ.get("MYSQL_URL") or os.environ.get("DATABASE_URL")
if _url and _url.startswith("mysql"):
    _u = urlparse(_url)
    DB_HOST = _u.hostname or DB_HOST
    DB_PORT = _u.port or DB_PORT
    DB_USER = unquote(_u.username or DB_USER)
    DB_PASSWORD = unquote(_u.password or "")
    DB_NAME = (_u.path or "").lstrip("/") or DB_NAME

# ---------------------------------------------------------------- servidor
PORT = int(os.environ.get("PORT", 5000))
SECRET_KEY = os.environ.get("SECRET_KEY", "cambiar-esta-clave-english-quest-ies7")

# Dirección que va en el QR. Vacía = se detecta sola (IP del Wi-Fi en tu compu, dominio en Railway).
PUBLIC_URL = os.environ.get("PUBLIC_URL", "")
if not PUBLIC_URL and os.environ.get("RAILWAY_PUBLIC_DOMAIN"):
    PUBLIC_URL = "https://" + os.environ["RAILWAY_PUBLIC_DOMAIN"]
