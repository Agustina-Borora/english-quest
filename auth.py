"""Login único para profe y alumnos, registro de profe y salida."""
from flask import Blueprint, Response, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

import db
from common import username_taken
from seed import seed_teacher

bp = Blueprint("auth", __name__)


def safe_next(target):
    """Solo permite redirigir a páginas internas."""
    if target and target.startswith("/") and not target.startswith("//"):
        return target
    return None


@bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if session.get("role") == "teacher":
            return redirect(url_for("teacher.home"))
        if session.get("role") == "student":
            return redirect(safe_next(request.args.get("next")) or url_for("student.home"))
        return render_template("login.html", next=request.args.get("next", ""),
                               join_code=_code_from_next(request.args.get("next", "")))

    username = request.form.get("username", "").strip().lower()
    secret = request.form.get("password", "").strip()
    nxt = safe_next(request.form.get("next"))

    teacher = db.query_one("SELECT * FROM teachers WHERE username=%s", (username,))
    if teacher and check_password_hash(teacher["password_hash"], secret):
        session.clear()
        session.update(role="teacher", teacher_id=teacher["id"], name=teacher["name"])
        return redirect(nxt if nxt and nxt.startswith("/profe") else url_for("teacher.home"))

    student = db.query_one("SELECT * FROM students WHERE username=%s", (username,))
    if student and student["pin"] == secret:
        session.clear()
        session.update(role="student", student_id=student["id"], teacher_id=student["teacher_id"],
                       name=student["name"])
        db.execute("UPDATE students SET last_seen=NOW() WHERE id=%s", (student["id"],))
        return redirect(nxt or url_for("student.home"))

    flash("Usuario o contraseña incorrectos 😕", "error")
    return render_template("login.html", next=request.form.get("next", ""), username=username,
                           join_code=_code_from_next(request.form.get("next", "")))


def _code_from_next(nxt):
    if nxt and "code=" in nxt:
        return nxt.split("code=")[-1][:6]
    return ""


@bp.route("/registro", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    name = request.form.get("name", "").strip()[:80]
    username = request.form.get("username", "").strip().lower()[:40]
    password = request.form.get("password", "")
    error = None
    if not name or not username or not password:
        error = "Completá todos los campos."
    elif not username.isalnum():
        error = "El usuario solo puede tener letras y números (sin espacios)."
    elif len(password) < 6:
        error = "La contraseña tiene que tener al menos 6 caracteres."
    elif username_taken(username):
        error = "Ese usuario ya existe. Probá con otro."
    if error:
        flash(error, "error")
        return render_template("register.html", name=name, username=username)

    tid = db.execute("INSERT INTO teachers (name, username, password_hash) VALUES (%s,%s,%s)",
                     (name, username, generate_password_hash(password)))
    seed_teacher(tid)
    session.clear()
    session.update(role="teacher", teacher_id=tid, name=name)
    flash("¡Cuenta creada! Te cargamos temas, lecciones y juegos de ejemplo para empezar 🎉", "ok")
    return redirect(url_for("teacher.home"))


@bp.route("/salir")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


@bp.route("/jugar")
def join_link():
    """Link del QR: si el alumno no inició sesión, primero lo manda al login."""
    code = request.args.get("code", "")[:6]
    if session.get("role") == "student":
        return redirect(url_for("student.play", code=code))
    return redirect(url_for("auth.login", next=f"/alumno/jugar?code={code}"))


@bp.route("/escenario/<int:scene_id>/imagen")
def scene_image(scene_id):
    """Imagen de un escenario propio. La ven la profe que lo creó y sus alumnos."""
    row = db.query_one("SELECT image, mime FROM custom_scenes WHERE id=%s AND teacher_id=%s",
                       (scene_id, session.get("teacher_id")))
    if not row:
        abort(404)
    resp = Response(row["image"], mimetype=row["mime"])
    resp.headers["Cache-Control"] = "private, max-age=86400"
    return resp
