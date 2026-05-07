"""
FOCUS Platform — Routes Modules, Quiz, Coach IA, Certificats
=============================================================
Ajoute ces routes dans app.py ou importe ce fichier.
"""

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify, send_file
)
from database.db import (
    get_all_modules, get_module_by_slug, get_lessons_by_module,
    get_quiz_questions, get_user_progress, mark_lesson_started,
    mark_lesson_completed, get_module_completion_rate,
    get_user_module_progress, award_badge, check_and_award_module_badge,
    issue_certificate, get_user_certificates, verify_certificate,
    get_or_create_ai_session, update_ai_session, get_ai_message_count_today,
    MAX_AI_MESSAGES_PER_DAY, add_points, log_activity, get_user_by_id,
    get_leaderboard, get_user_badges, get_user_notifications,
    mark_notifications_read
)
import json
import os
import requests
from datetime import datetime


# ── Helper ──────────────────────────────
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Connecte-toi pour accéder à cette page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def get_current_user():
    if "user_id" in session:
        return get_user_by_id(session["user_id"])
    return None


# ─────────────────────────────────────────
# CATALOGUE DES MODULES
# ─────────────────────────────────────────

def modules_catalogue():
    user     = get_current_user()
    modules  = get_all_modules()
    progress = get_user_module_progress(user["id"])
    certs    = get_user_certificates(user["id"])
    cert_slugs = [c["module_id"] for c in certs]
    return render_template("modules/catalogue.html",
        user=user, modules=modules,
        progress=progress, cert_slugs=cert_slugs
    )


# ─────────────────────────────────────────
# DÉTAIL D'UN MODULE
# ─────────────────────────────────────────

def module_detail(slug):
    user   = get_current_user()
    module = get_module_by_slug(slug)
    if not module:
        flash("Module introuvable.", "error")
        return redirect(url_for("modules_catalogue"))

    lessons  = get_lessons_by_module(module["id"])
    completed, total, pct = get_module_completion_rate(user["id"], module["id"])

    # Progression par leçon
    lesson_progress = {}
    for l in lessons:
        prog = get_user_progress(user["id"], l["id"])
        lesson_progress[l["id"]] = prog["status"] if prog else "not_started"

    return render_template("modules/detail.html",
        user=user, module=module, lessons=lessons,
        completed=completed, total=total, pct=pct,
        lesson_progress=lesson_progress
    )


# ─────────────────────────────────────────
# UNE LEÇON
# ─────────────────────────────────────────

def lesson_view(slug, lesson_id):
    user   = get_current_user()
    module = get_module_by_slug(slug)
    if not module:
        return redirect(url_for("modules_catalogue"))

    lessons = get_lessons_by_module(module["id"])
    lesson  = next((l for l in lessons if l["id"] == lesson_id), None)
    if not lesson:
        flash("Leçon introuvable.", "error")
        return redirect(url_for("module_detail", slug=slug))

    # Marquer comme commencée
    mark_lesson_started(user["id"], lesson_id)

    # Leçon suivante / précédente
    idx       = lessons.index(lesson)
    prev_lesson = lessons[idx - 1] if idx > 0 else None
    next_lesson = lessons[idx + 1] if idx < len(lessons) - 1 else None

    questions = []
    if lesson["lesson_type"] == "quiz":
        questions = get_quiz_questions(lesson_id)

    progress = get_user_progress(user["id"], lesson_id)

    return render_template("modules/lesson.html",
        user=user, module=module, lesson=lesson,
        lessons=lessons, questions=questions,
        prev_lesson=prev_lesson, next_lesson=next_lesson,
        progress=progress, lesson_index=idx
    )


# ─────────────────────────────────────────
# SOUMETTRE UN QUIZ
# ─────────────────────────────────────────

def submit_quiz(slug, lesson_id):
    user   = get_current_user()
    module = get_module_by_slug(slug)
    if not module:
        return jsonify({"error": "Module introuvable"}), 404

    questions = get_quiz_questions(lesson_id)
    if not questions:
        return jsonify({"error": "Aucune question"}), 404

    answers   = request.json.get("answers", {})
    correct   = 0
    results   = []

    for q in questions:
        qid         = str(q["id"])
        user_answer = answers.get(qid, "").lower()
        is_correct  = user_answer == q["correct_option"]
        if is_correct:
            correct += 1
        results.append({
            "question_id":  q["id"],
            "correct":      is_correct,
            "user_answer":  user_answer,
            "right_answer": q["correct_option"],
            "explanation":  q["explanation"],
            "question":     q["question_text"],
        })

    score   = round((correct / len(questions)) * 100)
    passed  = score >= module["passing_score"]

    if passed:
        mark_lesson_completed(user["id"], lesson_id, score)
        add_points(user["id"], score // 10)
        log_activity(user["id"], "quiz_passed", f"Score {score}% — leçon {lesson_id}")

        # Vérifier si tout le module est complété
        completed, total, pct = get_module_completion_rate(user["id"], module["id"])
        module_done = completed == total and total > 0

        cert_uid = None
        if module_done:
            check_and_award_module_badge(user["id"], slug)
            cert_uid = issue_certificate(user["id"], module["id"], score)
            log_activity(user["id"], "certificate_issued", f"Certificat {cert_uid}")

        return jsonify({
            "passed":      True,
            "score":       score,
            "correct":     correct,
            "total":       len(questions),
            "results":     results,
            "module_done": module_done,
            "cert_uid":    cert_uid,
        })
    else:
        log_activity(user["id"], "quiz_failed", f"Score {score}% — leçon {lesson_id}")
        return jsonify({
            "passed":  False,
            "score":   score,
            "correct": correct,
            "total":   len(questions),
            "results": results,
            "needed":  module["passing_score"],
        })


# ─────────────────────────────────────────
# COACH IA
# ─────────────────────────────────────────

COACH_PROMPTS = {
    "leadership": """Tu es le Coach IA FOCUS spécialisé en Leadership Transformationnel.
Tu aides les étudiants burkinabè à comprendre et appliquer le modèle de Bass (4 piliers : Influence Idéalisée, Motivation Inspirante, Stimulation Intellectuelle, Considération Individuelle).
Tu peux simuler des scénarios de leadership : conflit dans une équipe, démotivation d'un membre, gestion d'une crise dans un lycée, etc.
Tu donnes des feedbacks bienveillants et constructifs. Tu fais référence aux valeurs FOCUS : Patriotisme, Intégrité, Excellence, Service, Relève.
Réponds toujours en français. Sois encourageant, précis et ancré dans la réalité africaine.""",

    "project": """Tu es le Coach IA FOCUS spécialisé en Gestion de Projet.
Tu joues parfois le rôle d'un client exigeant ou d'un directeur d'école pour tester les réflexes du chef de projet.
Tu enseignes le cycle de vie d'un projet : Initiation, Planification, Exécution, Contrôle, Clôture.
Tu poses des questions difficiles, tu simules des imprévus (budget réduit, délai raccourci, membre absent).
Réponds toujours en français. Sois concret et pratique.""",

    "python": """Tu es le Coach IA FOCUS spécialisé en Python pour débutants.
Tu corriges le code Python, expliques les erreurs clairement, et proposes des exercices progressifs adaptés au niveau A2.
Tu utilises des exemples simples et concrets (calcul de notes, liste d'élèves, etc.).
Quand l'utilisateur partage du code, analyse-le et explique chaque erreur.
Réponds toujours en français. Sois patient et pédagogue.""",

    "english": """You are the FOCUS AI Coach specialized in English for African students.
Your role is to practice conversational English with FOCUS members from Burkina Faso.
You correct grammar errors gently, explain mistakes, and encourage the student.
You discuss topics relevant to leadership, technology, and African development.
Always respond in English, but if the student writes in French, gently remind them to try in English and help them rephrase.
Be encouraging, patient, and use simple vocabulary (A2-B1 level).""",
}

def ai_coach(slug):
    user = get_current_user()
    module = get_module_by_slug(slug)
    if not module:
        return jsonify({"error": "Module introuvable"}), 404

    data        = request.json
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Message vide"}), 400

    # Limite journalière
    count = get_ai_message_count_today(user["id"], slug)
    if count >= MAX_AI_MESSAGES_PER_DAY:
        return jsonify({
            "error": f"Limite journalière atteinte ({MAX_AI_MESSAGES_PER_DAY} messages/jour). Reviens demain ! 💪"
        }), 429

    # Session IA
    ai_session   = get_or_create_ai_session(user["id"], slug)
    history      = json.loads(ai_session["messages"])
    system_prompt = COACH_PROMPTS.get(slug, COACH_PROMPTS["leadership"])

    # Ajouter le message utilisateur
    history.append({"role": "user", "content": user_message})

    # Appel API Anthropic
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type":      "application/json",
                "x-api-key":         os.environ.get("ANTHROPIC_API_KEY", ""),
                "anthropic-version": "2023-06-01",
            },
            json={
                "model":      "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "system":     system_prompt,
                "messages":   history[-10:],  # 10 derniers messages max
            },
            timeout=30,
        )
        response.raise_for_status()
        ai_reply = response.json()["content"][0]["text"]

    except requests.exceptions.Timeout:
        return jsonify({"error": "Le Coach IA met trop de temps à répondre. Réessaie."}), 504
    except Exception as e:
        return jsonify({"error": "Coach IA indisponible pour le moment. Réessaie dans quelques instants."}), 503

    # Sauvegarder l'historique
    history.append({"role": "assistant", "content": ai_reply})
    update_ai_session(ai_session["id"], json.dumps(history))
    log_activity(user["id"], "ai_message", f"Coach {slug} — message #{count+1}")

    return jsonify({
        "reply":      ai_reply,
        "count":      count + 1,
        "remaining":  MAX_AI_MESSAGES_PER_DAY - count - 1,
    })


# ─────────────────────────────────────────
# CERTIFICATS
# ─────────────────────────────────────────

def my_certificates():
    user  = get_current_user()
    certs = get_user_certificates(user["id"])
    return render_template("modules/certificates.html", user=user, certs=certs)


def download_certificate(uid):
    """Generate and download a PDF certificate."""
    cert = verify_certificate(uid)
    if not cert:
        flash("Certificat introuvable ou invalide.", "error")
        return redirect(url_for("my_certificates"))

    # Generate PDF
    pdf_path = generate_certificate_pdf(cert)
    return send_file(pdf_path, as_attachment=True,
                     download_name=f"Certificat_FOCUS_{uid}.pdf")


def verify_cert_page(uid):
    cert = verify_certificate(uid)
    return render_template("modules/verify.html", cert=cert, uid=uid)


def generate_certificate_pdf(cert):
    """Generate a PDF certificate using ReportLab."""
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.pdfgen import canvas
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph
        from reportlab.lib.enums import TA_CENTER
    except ImportError:
        raise Exception("ReportLab non installé. Lance : py -m pip install reportlab")

    os.makedirs("certificates", exist_ok=True)
    pdf_path = f"certificates/{cert['certificate_uid']}.pdf"

    if os.path.exists(pdf_path):
        return pdf_path

    w, h    = landscape(A4)
    c       = canvas.Canvas(pdf_path, pagesize=landscape(A4))
    TEAL    = colors.HexColor("#1A7A6E")
    TEAL_D  = colors.HexColor("#0F5A50")
    GOLD    = colors.HexColor("#C8A84B")
    INK     = colors.HexColor("#1A1A2E")
    LIGHT   = colors.HexColor("#E6F5F3")

    # Background
    c.setFillColor(colors.white)
    c.rect(0, 0, w, h, fill=1, stroke=0)

    # Top banner
    c.setFillColor(TEAL_D)
    c.rect(0, h - 3*cm, w, 3*cm, fill=1, stroke=0)

    # Gold accent line
    c.setFillColor(GOLD)
    c.rect(0, h - 3.15*cm, w, 0.15*cm, fill=1, stroke=0)

    # Bottom banner
    c.setFillColor(TEAL_D)
    c.rect(0, 0, w, 2*cm, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(0, 2*cm, w, 0.12*cm, fill=1, stroke=0)

    # Left accent bar
    c.setFillColor(TEAL)
    c.rect(0, 0, 0.8*cm, h, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(0.8*cm, 0, 0.15*cm, h, fill=1, stroke=0)

    # Right accent bar
    c.setFillColor(TEAL)
    c.rect(w - 0.8*cm, 0, 0.8*cm, h, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(w - 0.95*cm, 0, 0.15*cm, h, fill=1, stroke=0)

    # FOCUS logo text in banner
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(w/2, h - 2*cm, "FOCUS")
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.HexColor("#AADDCC"))
    c.drawCentredString(w/2, h - 2.55*cm, "LEADERSHIP & DÉVELOPPEMENT PERSONNEL  ·  BURKINA FASO")

    # CERTIFICAT title
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(w/2, h - 4.5*cm, "✦  CERTIFICAT DE RÉUSSITE  ✦")

    # Gold separator
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.line(w/2 - 6*cm, h - 5*cm, w/2 + 6*cm, h - 5*cm)

    # "Certifie que"
    c.setFillColor(colors.HexColor("#64748B"))
    c.setFont("Helvetica-Oblique", 13)
    c.drawCentredString(w/2, h - 6*cm, "La Coordination FOCUS certifie que")

    # Recipient name
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(w/2, h - 7.5*cm, cert["full_name"])

    # Underline name
    name_w = c.stringWidth(cert["full_name"], "Helvetica-Bold", 32)
    c.setStrokeColor(TEAL)
    c.setLineWidth(1)
    c.line(w/2 - name_w/2, h - 7.8*cm, w/2 + name_w/2, h - 7.8*cm)

    # "a complété avec succès"
    c.setFillColor(colors.HexColor("#64748B"))
    c.setFont("Helvetica-Oblique", 13)
    c.drawCentredString(w/2, h - 8.8*cm, "a complété avec succès le module")

    # Module name
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(w/2, h - 10*cm, cert["module_title"])

    # Score badge
    score_x = w/2
    c.setFillColor(LIGHT)
    c.roundRect(score_x - 3*cm, h - 12*cm, 6*cm, 1.6*cm, 0.4*cm, fill=1, stroke=0)
    c.setStrokeColor(TEAL)
    c.setLineWidth(1)
    c.roundRect(score_x - 3*cm, h - 12*cm, 6*cm, 1.6*cm, 0.4*cm, fill=0, stroke=1)
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(score_x, h - 11.1*cm, f"Score : {cert['final_score']}%")
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#64748B"))
    c.drawCentredString(score_x, h - 11.6*cm, "avec mention")

    # Date + UID
    issued = cert["issued_at"][:10]
    c.setFillColor(colors.HexColor("#64748B"))
    c.setFont("Helvetica", 10)
    c.drawCentredString(w/2, h - 13.2*cm, f"Délivré le {issued}  ·  Réf : {cert['certificate_uid']}")

    # Bottom pillars
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    pillars = ["PATRIOTISME", "INTÉGRITÉ", "EXCELLENCE", "SERVICE", "RELÈVE"]
    spacing = w / (len(pillars) + 1)
    for i, p in enumerate(pillars):
        c.drawCentredString(spacing * (i + 1), 1.2*cm, p)

    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(w/2, 0.5*cm, f"Vérifiable sur : focus-bf.org/verify/{cert['certificate_uid']}")

    c.save()
    return pdf_path
