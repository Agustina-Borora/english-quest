# ⭐ English Quest

Plataforma para aprender inglés jugando (primaria 4.º a 7.º), hecha en **Python + Flask + MySQL**.

## ¿Qué tiene?

### Un solo inicio de sesión
- **Profe**: usuario + contraseña (se crea la cuenta desde "Crear cuenta de profe").
- **Alumno**: usuario + PIN de 4 números (se los da la profe).

### 👩‍🏫 Panel de la profe
| Sección | Qué hace |
|---|---|
| **Inicio** | Resumen: alumnos, lecciones, temas, juegos, quién tiene más estrellas, últimas partidas. |
| **Temas** | Grupos de palabras (inglés, traducción, dibujo/emoji y oración). Se pueden crear y editar. |
| **Lecciones** | La "clase". Se elige el **escenario** (casa, súper, escuela, parque, zoológico, playa o uno propio), los **temas** y **cómo se presenta**: con **todos los temas juntos** (las mismas actividades para todas las palabras) o **cada tema por separado** (cada tema con su escenario, sus actividades y su orden). Actividades: Explorar, Tarjetas, Leer y escuchar, Escribir, Desafío final. Se puede asignar a un curso, ocultar/publicar y ver como alumno. |
| **Escenarios** | Además de los dibujados, la profe crea **escenarios propios con imágenes de su compu** (se achican solas antes de subirse) y puede tocar la imagen para marcar **dónde aparece cada palabra** en Explorar. Se pueden editar y borrar. |
| **Juegos rápidos** | Se preparan de antemano y se usan cuando quieras. Se escriben a mano o se **generan solos desde un tema**. Se pueden duplicar. Al tocar **Jugar** se crea un código de 6 números + QR **nuevos**; al terminar quedan bloqueados. Los resultados quedan guardados. |
| **Alumnos** | Se cargan pegando la lista del curso. Cada uno recibe usuario y PIN. Hay **tarjetas de acceso para imprimir**. |
| **Progreso** | Cuántos terminaron cada lección, estrellas por alumno y lección, juegos jugados, % de aciertos, monedas y detalle por alumno. |

### 🧒 Panel del alumno
- **Personita personalizable** ("Cambiar mi look"): piel, peinado, color de pelo, ojos, ropa, colores y accesorios.
- **⚡ Clase rápida: ¿cómo me uno?** con los 3 pasos explicados y el lugar para escribir el código (o escanear el QR).
- **🗺️ Mi aventura**: un mapa donde cada lección es un lugar dibujado. La personita camina hasta el lugar elegido.
- En cada lección: escena dibujada, pronunciación en inglés 🔊, estrellas por actividad y monedas 🪙.

## Cómo ejecutarlo (Windows + Laragon)

1. Abrí **Laragon** y tocá **Iniciar todo** (tiene que estar MySQL en verde).
2. Abrí una terminal en la carpeta del proyecto (por ejemplo `C:\laragon\www\english_quest`).
   En Laragon podés usar el botón **Terminal**.
3. Instalá las librerías (solo la primera vez):
   ```
   pip install -r requirements.txt
   ```
4. Ejecutá:
   ```
   python app.py
   ```
   La **base de datos `english_quest` y todas las tablas se crean solas**.
5. Abrí `http://localhost:5000`, tocá **Crear cuenta de profe** y listo: te carga temas, lecciones y juegos de ejemplo.

> El juego corre con su propio servidor de Python en el puerto 5000; no usa el Apache de Laragon, solo su MySQL.

### Si tu MySQL tiene contraseña
Por defecto usa el de Laragon: usuario `root` **sin contraseña**. Si el tuyo tiene, cambiala en `config.py` (`DB_PASSWORD`).

### Para que entren los celulares
- La consola muestra una dirección tipo `http://192.168.x.x:5000`. El QR ya la trae.
- Los celulares tienen que estar en **la misma red Wi-Fi** que la compu.
- Si Windows pregunta por el Firewall, tocá **Permitir acceso**.

## Subirlo a internet (Railway)
El proyecto ya está preparado para Railway:
- `Procfile` → Railway lo arranca con **Gunicorn** (un solo proceso, porque las partidas en vivo viven en memoria).
- `.python-version` → versión de Python.
- `config.py` lee solo las variables de Railway: `MYSQL_URL`, `SECRET_KEY`, `PORT` y `RAILWAY_PUBLIC_DOMAIN` (esta última hace que el QR use tu dominio).
- Las tablas se crean solas al arrancar.

Pasos resumidos:
1. Subí la carpeta a un repositorio de GitHub.
2. En Railway: **New Project → Deploy from GitHub repo** y elegí el repositorio.
3. Agregá una base: **+ Create → Database → MySQL**.
4. En el servicio de la app, pestaña **Variables**, agregá:
   - `MYSQL_URL` = `${{MySQL.MYSQL_URL}}`
   - `SECRET_KEY` = un texto largo inventado
5. En **Settings → Networking → Generate Domain** (si pide puerto: `8080`).
6. Abrí el dominio y creá la cuenta de profe.

Cada vez que hagas `git push`, Railway vuelve a publicar solo.

## Base de datos (MySQL)
El archivo `database.sql` tiene el script completo, por si querés ver o crear las tablas desde HeidiSQL o phpMyAdmin.

| Tabla | Guarda |
|---|---|
| `teachers` | Profes (la contraseña va encriptada) |
| `students` | Alumnos: curso, usuario, PIN, personita, monedas |
| `topics` / `words` | Temas y sus palabras |
| `lessons` / `lesson_topics` | Lecciones: escenario, actividades en orden, curso, si va tema por tema; y qué temas usan (con su orden, escenario y actividades) |
| `custom_scenes` | Escenarios propios de cada profe: nombre, imagen y lugares de las palabras |
| `lesson_progress` | Progreso de cada alumno en cada actividad |
| `quick_games` / `quick_questions` | Juegos rápidos y sus preguntas |
| `game_sessions` / `game_results` | Cada partida jugada (con su código, que no se reutiliza) y los resultados |

## Librerías usadas
| Librería | Para qué |
|---|---|
| **Flask** | Servidor web, páginas y sesiones (login) |
| **Flask-SocketIO** | Clase rápida en tiempo real |
| **simple-websocket** | Conexión WebSocket para Flask-SocketIO |
| **PyMySQL** | Conexión con MySQL |
| **segno** | Generar los códigos QR |
| **Werkzeug** (viene con Flask) | Encriptar las contraseñas |
| **Gunicorn** | Servidor de producción en Railway (en Windows no se usa) |
| Socket.IO (JS, incluido en `static/js`) | El lado del navegador del tiempo real |
| Web Speech API (del navegador) | La voz que pronuncia en inglés |

## Estructura
```
english_quest/
├── app.py            # Arranca todo y crea la base de datos
├── config.py         # Datos de conexión a MySQL y puerto
├── db.py             # Conexión y tablas (PyMySQL)
├── seed.py           # Contenido de ejemplo para cada profe nueva
├── common.py         # Permisos, actividades, escenarios, ayudas
├── auth.py           # Login único, registro de profe, link del QR
├── teacher.py        # Panel de la profe
├── student.py        # Panel del alumno
├── live.py           # Clase rápida en vivo (código + QR)
├── database.sql      # Script SQL de referencia
├── Procfile          # Cómo arranca en Railway
├── .python-version   # Versión de Python para Railway
├── .gitignore        # Lo que no se sube a GitHub
├── templates/        # Páginas HTML (teacher/ y student/)
└── static/
    ├── css/          # style.css, panel.css, kid.css
    └── js/           # avatar.js (personitas), scenes.js (escenarios), lesson.js, map.js, live_*.js
```
