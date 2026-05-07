"""
FOCUS Leadership Platform — Application Principale v2
======================================================
Lancement : py app.py
Accès      : http://localhost:5000
"""

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify, send_file
)
from database.db import (
    get_all_badges,
    create_user, authenticate_user, get_user_by_id,
    award_badge, log_activity, get_user_notifications,
    get_admin_stats, get_all_users, update_user_status,
    get_user_by_email, get_all_modules, get_module_by_slug,
    get_lessons_by_module, get_quiz_questions, get_user_progress,
    mark_lesson_started, mark_lesson_completed,
    get_module_completion_rate, get_user_module_progress,
    check_and_award_module_badge, issue_certificate,
    get_user_certificates, verify_certificate,
    get_or_create_ai_session, update_ai_session,
    get_ai_message_count_today, MAX_AI_MESSAGES_PER_DAY,
    add_points, get_leaderboard, get_user_badges,
    get_inactive_members
)
import json, os, requests
from functools import wraps

app = Flask(__name__)
app.secret_key = "FOCUS-SECRET-KEY-2025-BF"

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Connecte-toi pour accéder à cette page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        if session.get("role") != "admin":
            flash("Accès réservé aux coordinateurs FOCUS.", "error")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated

def get_current_user():
    if "user_id" in session:
        return get_user_by_id(session["user_id"])
    return None

COACH_PROMPTS = {
    "leadership": "Tu es le Coach IA FOCUS spécialisé en Leadership Transformationnel. Tu aides les étudiants burkinabè à comprendre le modèle de Bass (4 piliers). Tu simules des scénarios de leadership réels. Tu donnes des feedbacks bienveillants. Réponds toujours en français.",
    "project":    "Tu es le Coach IA FOCUS spécialisé en Gestion de Projet. Tu joues parfois le rôle d'un client exigeant. Tu enseignes le cycle de vie d'un projet et simules des imprévus. Réponds toujours en français.",
    "python":     "Tu es le Coach IA FOCUS spécialisé en Python pour débutants. Tu corriges le code, expliques les erreurs clairement avec des exemples simples. Sois patient et pédagogue. Réponds toujours en français.",
    "english":    "You are the FOCUS AI Coach for English practice. Practice conversational English with students from Burkina Faso. Correct grammar gently. Use simple A2-B1 vocabulary. Always respond in English.",
}

# ─────────────────────────────────────────
# PUBLIQUES
# ─────────────────────────────────────────

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        full_name     = request.form.get("full_name", "").strip()
        email         = request.form.get("email", "").strip().lower()
        password      = request.form.get("password", "")
        confirm       = request.form.get("confirm_password", "")
        establishment = request.form.get("establishment", "").strip()
        city          = request.form.get("city", "").strip()
        if not all([full_name, email, password, confirm]):
            flash("Tous les champs obligatoires doivent être remplis.", "error")
            return render_template("register.html")
        if len(password) < 8:
            flash("Le mot de passe doit contenir au moins 8 caractères.", "error")
            return render_template("register.html")
        if password != confirm:
            flash("Les mots de passe ne correspondent pas.", "error")
            return render_template("register.html")
        user_id = create_user(full_name, email, password, establishment, city)
        if user_id is None:
            flash("Cette adresse email est déjà utilisée.", "error")
            return render_template("register.html")
        award_badge(user_id, "eveille")
        log_activity(user_id, "register", f"Nouveau membre : {full_name}")
        flash("🎉 Inscription réussie ! Ton compte est en attente de validation.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = authenticate_user(email, password)
        if user is None:
            existing = get_user_by_email(email)
            if existing and existing["status"] == "pending":
                flash("Ton compte est en attente de validation.", "warning")
            elif existing and existing["status"] == "suspended":
                flash("Ton compte a été suspendu.", "error")
            else:
                flash("Email ou mot de passe incorrect.", "error")
            return render_template("login.html")
        session["user_id"] = user["id"]
        session["role"]    = user["role"]
        session["name"]    = user["full_name"]
        log_activity(user["id"], "login")
        flash(f"Bienvenue, {user['full_name'].split()[0]} 👋", "success")
        if user["role"] == "admin":
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    if "user_id" in session:
        log_activity(session["user_id"], "logout")
    session.clear()
    flash("Tu as été déconnecté.", "info")
    return redirect(url_for("login"))

# ─────────────────────────────────────────
# MEMBRE
# ─────────────────────────────────────────

@app.route("/dashboard")
@login_required
def dashboard():
    user          = get_current_user()
    progress      = get_user_module_progress(user["id"])
    badges        = get_user_badges(user["id"])
    leaderboard   = get_leaderboard(5)
    notifications = get_user_notifications(user["id"], unread_only=True)
    return render_template("dashboard.html",
        user=user, progress=progress,
        badges=badges, leaderboard=leaderboard,
        notifications=notifications)

@app.route("/modules")
@login_required
def modules_catalogue():
    user     = get_current_user()
    modules  = get_all_modules()
    progress = get_user_module_progress(user["id"])
    certs    = get_user_certificates(user["id"])
    cert_mids = [c["module_id"] for c in certs]
    return render_template("modules/catalogue.html",
        user=user, modules=modules,
        progress=progress, cert_mids=cert_mids)

@app.route("/modules/<slug>")
@login_required
def module_detail(slug):
    user   = get_current_user()
    module = get_module_by_slug(slug)
    if not module:
        flash("Module introuvable.", "error")
        return redirect(url_for("modules_catalogue"))
    lessons               = get_lessons_by_module(module["id"])
    completed, total, pct = get_module_completion_rate(user["id"], module["id"])
    lesson_progress       = {}
    for l in lessons:
        prog = get_user_progress(user["id"], l["id"])
        lesson_progress[l["id"]] = prog["status"] if prog else "not_started"
    return render_template("modules/detail.html",
        user=user, module=module, lessons=lessons,
        completed=completed, total=total, pct=pct,
        lesson_progress=lesson_progress)

@app.route("/modules/<slug>/lesson/<int:lesson_id>")
@login_required
def lesson_view(slug, lesson_id):
    user    = get_current_user()
    module  = get_module_by_slug(slug)
    if not module:
        return redirect(url_for("modules_catalogue"))
    lessons = get_lessons_by_module(module["id"])
    lesson  = next((l for l in lessons if l["id"] == lesson_id), None)
    if not lesson:
        return redirect(url_for("module_detail", slug=slug))
    mark_lesson_started(user["id"], lesson_id)
    idx         = lessons.index(lesson)
    prev_lesson = lessons[idx-1] if idx > 0 else None
    next_lesson = lessons[idx+1] if idx < len(lessons)-1 else None
    questions   = get_quiz_questions(lesson_id) if lesson["lesson_type"] == "quiz" else []
    progress    = get_user_progress(user["id"], lesson_id)
    return render_template("modules/lesson.html",
        user=user, module=module, lesson=lesson,
        lessons=lessons, questions=questions,
        prev_lesson=prev_lesson, next_lesson=next_lesson,
        progress=progress, lesson_index=idx)

@app.route("/modules/<slug>/lesson/<int:lesson_id>/complete", methods=["POST"])
@login_required
def complete_lesson(slug, lesson_id):
    user = get_current_user()
    mark_lesson_completed(user["id"], lesson_id)
    add_points(user["id"], 20)
    return jsonify({"success": True})

@app.route("/modules/<slug>/lesson/<int:lesson_id>/quiz", methods=["POST"])
@login_required
def submit_quiz(slug, lesson_id):
    user      = get_current_user()
    module    = get_module_by_slug(slug)
    questions = get_quiz_questions(lesson_id)
    if not questions:
        return jsonify({"error": "Aucune question"}), 404
    answers = request.json.get("answers", {})
    correct = 0
    results = []
    for q in questions:
        user_answer = answers.get(str(q["id"]), "").lower()
        is_correct  = user_answer == q["correct_option"]
        if is_correct:
            correct += 1
        results.append({"question_id": q["id"], "correct": is_correct,
                        "user_answer": user_answer, "right_answer": q["correct_option"],
                        "explanation": q["explanation"], "question": q["question_text"]})
    score  = round((correct / len(questions)) * 100)
    passed = score >= module["passing_score"]
    if passed:
        mark_lesson_completed(user["id"], lesson_id, score)
        add_points(user["id"], score // 10)
        completed, total, pct = get_module_completion_rate(user["id"], module["id"])
        module_done = (completed == total and total > 0)
        cert_uid = None
        if module_done:
            check_and_award_module_badge(user["id"], slug)
            cert_uid = issue_certificate(user["id"], module["id"], score)
        return jsonify({"passed": True, "score": score, "correct": correct,
                        "total": len(questions), "results": results,
                        "module_done": module_done, "cert_uid": cert_uid})
    return jsonify({"passed": False, "score": score, "correct": correct,
                    "total": len(questions), "results": results,
                    "needed": module["passing_score"]})

# ─────────────────────────────────────────
# COACH IA
# ─────────────────────────────────────────

@app.route("/modules/<slug>/coach")
@login_required
def coach_page(slug):
    user   = get_current_user()
    module = get_module_by_slug(slug)
    if not module:
        return redirect(url_for("modules_catalogue"))
    count = get_ai_message_count_today(user["id"], slug)
    return render_template("modules/coach.html",
        user=user, module=module,
        count=count, max_count=MAX_AI_MESSAGES_PER_DAY)

@app.route("/modules/<slug>/coach/chat", methods=["POST"])
@login_required
def ai_chat(slug):
    user         = get_current_user()
    user_message = request.json.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Message vide"}), 400
    count = get_ai_message_count_today(user["id"], slug)
    if count >= MAX_AI_MESSAGES_PER_DAY:
        return jsonify({"error": f"Limite de {MAX_AI_MESSAGES_PER_DAY} messages/jour atteinte. Reviens demain ! 💪"}), 429
    ai_session    = get_or_create_ai_session(user["id"], slug)
    history       = json.loads(ai_session["messages"])
    system_prompt = COACH_PROMPTS.get(slug, COACH_PROMPTS["leadership"])
    history.append({"role": "user", "content": user_message})
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return jsonify({"error": "Clé API non configurée. Contacte l'administrateur."}), 503
    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json",
                     "x-api-key": api_key,
                     "anthropic-version": "2023-06-01"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": 1000,
                  "system": system_prompt, "messages": history[-10:]},
            timeout=30)
        resp.raise_for_status()
        ai_reply = resp.json()["content"][0]["text"]
    except Exception:
        return jsonify({"error": "Coach IA indisponible. Réessaie dans quelques instants."}), 503
    history.append({"role": "assistant", "content": ai_reply})
    update_ai_session(ai_session["id"], json.dumps(history))
    log_activity(user["id"], "ai_message", f"Coach {slug}")
    return jsonify({"reply": ai_reply, "count": count+1,
                    "remaining": MAX_AI_MESSAGES_PER_DAY - count - 1})

# ─────────────────────────────────────────
# CERTIFICATS
# ─────────────────────────────────────────

@app.route("/certificates")
@login_required
def my_certificates():
    user  = get_current_user()
    certs = get_user_certificates(user["id"])
    return render_template("modules/certificates.html", user=user, certs=certs)

@app.route("/certificates/<uid>/download")
@login_required
def download_certificate(uid):
    cert = verify_certificate(uid)
    if not cert:
        flash("Certificat introuvable.", "error")
        return redirect(url_for("my_certificates"))
    from routes_modules import generate_certificate_pdf
    pdf_path = generate_certificate_pdf(cert)
    return send_file(pdf_path, as_attachment=True,
                     download_name=f"Certificat_FOCUS_{uid}.pdf")

@app.route("/verify/<uid>")
def verify_cert(uid):
    cert = verify_certificate(uid)
    return render_template("modules/verify.html", cert=cert, uid=uid)

# ─────────────────────────────────────────
# ADMIN
# ─────────────────────────────────────────

@app.route("/admin")
@admin_required
def admin_dashboard():
    stats    = get_admin_stats()
    members  = get_all_users()
    inactive = get_inactive_members(14)
    return render_template("admin/dashboard.html",
        stats=stats, members=members, inactive=inactive)

@app.route("/admin/member/<int:user_id>/activate")
@admin_required
def activate_member(user_id):
    update_user_status(user_id, "active")
    user = get_user_by_id(user_id)
    log_activity(session["user_id"], "admin_activate", user["email"])
    flash(f"✅ Compte de {user['full_name']} activé.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/member/<int:user_id>/suspend")
@admin_required
def suspend_member(user_id):
    update_user_status(user_id, "suspended")
    user = get_user_by_id(user_id)
    log_activity(session["user_id"], "admin_suspend", user["email"])
    flash(f"⛔ Compte de {user['full_name']} suspendu.", "warning")
    return redirect(url_for("admin_dashboard"))

# ─────────────────────────────────────────
# LANCEMENT
# ─────────────────────────────────────────


@app.route('/profile')
def profile():
    user = get_current_user()
    if user is None:
        session.clear()
        return redirect(url_for('login'))
    from attestation_focus import ensure_tables, check_all_modules_completed, issue_global_attestation, get_user_certs_detail
    ensure_tables()
    all_completed, completed_count, total_count = check_all_modules_completed(user['id'])
    progress = get_user_module_progress(user['id'])
    certs = get_user_certs_detail(user['id'])
    cert_map = {c['module_id']: c for c in certs}
    all_badges_list = get_all_badges()
    earned = get_user_badges(user['id'])
    earned_ids = [b['id'] for b in earned]
    uid = issue_global_attestation(user['id']) if all_completed else None
    return render_template('profile.html', user=user,
        all_completed=all_completed, completed_count=completed_count,
        total_count=total_count, progress=progress, cert_map=cert_map,
        all_badges=all_badges_list, earned_badges=earned,
        earned_badge_ids=earned_ids, attestation_uid=uid)

@app.route('/attestation/download')
def download_attestation():
    user = get_current_user()
    if user is None:
        return redirect(url_for('login'))
    from attestation_focus import ensure_tables, check_all_modules_completed, issue_global_attestation, generate_attestation_pdf
    ensure_tables()
    all_done, _, _ = check_all_modules_completed(user['id'])
    if not all_done:
        flash('Complete tous les modules.', 'warning')
        return redirect(url_for('profile'))
    uid = issue_global_attestation(user['id'])
    pdf = generate_attestation_pdf(user['id'], uid)
    return send_file(pdf, as_attachment=True, download_name='Attestation_FOCUS.pdf')


if __name__ == "__main__":
    print("\n🚀  FOCUS Platform v2 démarrée")
    print("🌐  http://localhost:5000")
    print("🔑  Admin : admin@focus-bf.org  /  Focus@Admin2025!")
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if api_key:
        print("🤖  Coach IA : ✅ Clé API détectée")
    else:
        print("⚠️   Coach IA : set ANTHROPIC_API_KEY=ta_cle_api")
    print("─" * 50)
    app.run(debug=True, port=5000)
