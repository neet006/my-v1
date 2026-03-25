"""
app.py — Flask web server for A.M.A.T.S. Driver Safety System.

Structure:
  backend/   ← this file
  frontend/  ← HTML templates + static assets

Run from project root:
  python backend/app.py
  — or —
  python run.py
"""
import os
import sys

# ── Path setup ────────────────────────────────────────────────────────────────
# This file lives at: <project_root>/backend/app.py
BACKEND_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT  = os.path.dirname(BACKEND_DIR)
FRONTEND_DIR  = os.path.join(PROJECT_ROOT, "frontend")
TEMPLATES_DIR = os.path.join(FRONTEND_DIR, "templates")
STATIC_DIR    = os.path.join(FRONTEND_DIR, "static")

# Ensure both project root AND backend dir are importable
# so that `import db` works whether run as a module or directly
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, BACKEND_DIR)

# ── Import db using direct path-based import (avoids package confusion) ───────
import importlib.util as _ilu

def _load_db():
    spec = _ilu.spec_from_file_location("db", os.path.join(BACKEND_DIR, "db.py"))
    mod  = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_db = _load_db()

create_user      = _db.create_user
verify_user      = _db.verify_user
get_sessions     = _db.get_sessions
save_session     = _db.save_session
get_settings     = _db.get_settings
save_settings    = _db.save_settings
DEFAULT_SESSIONS = _db.DEFAULT_SESSIONS

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, jsonify, Response
)
from backend.camera_service import camera_monitor

app = Flask(
    __name__,
    template_folder=TEMPLATES_DIR,
    static_folder=STATIC_DIR,
)

# ── Secret key: fixed so sessions survive server restarts ─────────────────────
# Uses env var SECRET_KEY if set, otherwise a stable fallback.
# NEVER expose the fallback string in production; set SECRET_KEY env var instead.
app.secret_key = os.environ.get(
    "AMATS_SECRET_KEY",
    "amats-dev-secret-key-change-in-production-2026"
)


# ─── Auth helpers ─────────────────────────────────────────────────────────────

def logged_in():
    return "user_id" in session


def require_login(next_url=None):
    """Return a redirect to /login if not logged in, else None."""
    if not logged_in():
        login_url = url_for("login")
        if next_url:
            login_url += f"?next={next_url}"
        return redirect(login_url)
    return None


# ─── Pages ────────────────────────────────────────────────────────────────────

@app.route("/")
def landing():
    # Logged-in users go straight to dashboard
    if logged_in():
        return redirect(url_for("dashboard"))
    return render_template("landing.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if logged_in():
        return redirect(url_for("dashboard"))

    error = None
    if request.method == "POST":
        email    = (request.form.get("email")    or "").strip().lower()
        password = (request.form.get("password") or "")

        if not email or not password:
            error = "Please fill in all fields."
        else:
            user = verify_user(email, password)
            if user:
                session.clear()                          # prevent session fixation
                session["user_id"]    = user["id"]
                session["user_name"]  = user["name"]
                session["user_email"] = user["email"]
                # Honour ?next= redirect
                next_page = request.args.get("next") or url_for("dashboard")
                return redirect(next_page)
            else:
                error = "Invalid email or password."

    return render_template("login.html", error=error)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if logged_in():
        return redirect(url_for("dashboard"))

    error = None
    if request.method == "POST":
        name     = (request.form.get("name")             or "").strip()
        email    = (request.form.get("email")            or "").strip().lower()
        password = (request.form.get("password")         or "")
        confirm  = (request.form.get("confirm_password") or "")

        if not name or not email or not password or not confirm:
            error = "Please fill in all fields."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        elif password != confirm:
            error = "Passwords do not match."
        else:
            try:
                create_user(name, email, password)
                # Redirect to login with success flag
                return redirect(url_for("login") + "?registered=1")
            except ValueError as exc:
                error = str(exc)

    return render_template("signup.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/dashboard")
def dashboard():
    guard = require_login(request.path)
    if guard:
        return guard
    return render_template(
        "dashboard.html",
        user_name=session.get("user_name", "Driver"),
        active_tab="live",
    )


@app.route("/statistics")
def statistics():
    guard = require_login(request.path)
    if guard:
        return guard
    sessions_data = get_sessions(session["user_id"])
    return render_template(
        "statistics.html",
        user_name=session.get("user_name", "Driver"),
        sessions=sessions_data,
        sessions_json=sessions_data,
        active_tab="statistics",
    )


@app.route("/settings")
def settings():
    guard = require_login(request.path)
    if guard:
        return guard
    user_settings = get_settings(session["user_id"])
    return render_template(
        "settings.html",
        user_name=session.get("user_name", "Driver"),
        settings=user_settings,
        active_tab="settings",
    )


@app.route("/music")
def music():
    guard = require_login(request.path)
    if guard:
        return guard
    return render_template(
        "music.html",
        user_name=session.get("user_name", "Driver"),
        active_tab="music",
    )


@app.route("/shop")
def shop():
    return redirect(url_for("music"))


# ─── REST API ─────────────────────────────────────────────────────────────────

@app.route("/api/settings", methods=["POST"])
def api_save_settings():
    if not logged_in():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json(force=True, silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid payload"}), 400
    save_settings(session["user_id"], data)
    session["alert_email_recipient"] = str(data.get("alert_email_recipient") or "")
    return jsonify({"ok": True})


@app.route("/api/sessions", methods=["GET", "POST"])
def api_sessions():
    if not logged_in():
        return jsonify({"error": "Unauthorized"}), 401
    if request.method == "GET":
        return jsonify(get_sessions(session["user_id"]))

    data = request.get_json(force=True, silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid payload"}), 400

    session_record = {
        "date": str(data.get("date") or "Just now"),
        "duration": str(data.get("duration") or "0h 00m"),
        "alerts": int(data.get("alerts") or 0),
        "max_drowsiness": str(data.get("max_drowsiness") or "0%"),
        "status": str(data.get("status") or "Completed"),
        "status_class": str(data.get("status_class") or "completed"),
        "drowsy_events": int(data.get("drowsy_events") or 0),
        "sleep_events": int(data.get("sleep_events") or 0),
    }
    save_session(session["user_id"], session_record)
    return jsonify({"ok": True, "session": session_record})


@app.route("/api/monitor/start", methods=["POST"])
def api_monitor_start():
    if not logged_in():
        return jsonify({"error": "Unauthorized"}), 401
    result = camera_monitor.start()
    if not result.get("ok"):
        return jsonify(result), 500
    return jsonify(result)


@app.route("/api/monitor/status")
def api_monitor_status():
    if not logged_in():
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(camera_monitor.status())


@app.route("/api/monitor/stop", methods=["POST"])
def api_monitor_stop():
    if not logged_in():
        return jsonify({"error": "Unauthorized"}), 401
    summary = camera_monitor.stop()
    if not summary.get("already_stopped"):
        save_session(session["user_id"], {
            "date": summary["date"],
            "duration": summary["duration"],
            "alerts": summary["alerts"],
            "max_drowsiness": summary["max_drowsiness"],
            "status": summary["status"],
            "status_class": summary["status_class"],
            "drowsy_events": summary["drowsy_events"],
            "sleep_events": summary["sleep_events"],
        })
    return jsonify({"ok": True, "session": summary})


@app.route("/video_feed")
def video_feed():
    if not logged_in():
        return redirect(url_for("login"))
    return Response(
        camera_monitor.frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


# ─── 404 handler ──────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(_):
    return redirect(url_for("landing"))


# ─── Entrypoint ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n  ╔══════════════════════════════════════╗")
    print("  ║   A.M.A.T.S. Web Server              ║")
    print("  ║   Open: http://localhost:5000         ║")
    print("  ╚══════════════════════════════════════╝\n")
    app.run(debug=True, port=5000, use_reloader=True)
