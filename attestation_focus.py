import sqlite3, os, uuid
from datetime import datetime

DB_PATH = 'focus_platform.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA foreign_keys = ON')
    conn.row_factory = sqlite3.Row
    return conn

def ensure_tables():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS global_attestations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attestation_uid TEXT NOT NULL UNIQUE,
        user_id INTEGER NOT NULL,
        issued_at TEXT NOT NULL DEFAULT (datetime('now')),
        pdf_path TEXT,
        is_valid INTEGER NOT NULL DEFAULT 1)''')
    conn.commit()
    conn.close()

def check_all_modules_completed(user_id):
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) FROM modules WHERE is_published=1').fetchone()[0]
    completed = conn.execute('SELECT COUNT(*) FROM certificates WHERE user_id=? AND is_valid=1', (user_id,)).fetchone()[0]
    conn.close()
    return completed >= total, completed, total

def get_user_certs_detail(user_id):
    conn = get_db()
    certs = conn.execute('''SELECT c.*, m.title as module_title, m.icon as module_icon, m.color as module_color, m.slug
        FROM certificates c JOIN modules m ON c.module_id = m.id
        WHERE c.user_id=? AND c.is_valid=1 ORDER BY c.issued_at ASC''', (user_id,)).fetchall()
    conn.close()
    return certs

def issue_global_attestation(user_id):
    ensure_tables()
    conn = get_db()
    existing = conn.execute('SELECT * FROM global_attestations WHERE user_id=? AND is_valid=1', (user_id,)).fetchone()
    if existing:
        conn.close()
        return existing['attestation_uid']
    uid = 'FOCUS-GLOBAL-' + str(uuid.uuid4()).upper()[:8]
    conn.execute('INSERT INTO global_attestations (attestation_uid, user_id) VALUES (?, ?)', (uid, user_id))
    badge = conn.execute("SELECT * FROM badges WHERE slug='focus_certifie'").fetchone()
    if badge:
        try:
            conn.execute('INSERT INTO user_badges (user_id, badge_id, awarded_by) VALUES (?, ?, ?)', (user_id, badge['id'], 'system'))
            conn.execute('UPDATE users SET points = points + ? WHERE id=?', (badge['points_reward'], user_id))
        except:
            pass
    conn.commit()
    conn.close()
    return uid

def generate_attestation_pdf(user_id, attestation_uid):
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader

    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id=?', (user_id,)).fetchone()
    certs = get_user_certs_detail(user_id)
    conn.close()

    os.makedirs('certificates', exist_ok=True)
    pdf_path = f'certificates/attestation_focus_{attestation_uid}.pdf'
    if os.path.exists(pdf_path):
        return pdf_path

    w, h = landscape(A4)
    TEAL = colors.HexColor('#1A7A6E')
    TEAL_DARK = colors.HexColor('#0F5A50')
    GOLD = colors.HexColor('#C8A84B')
    GOLD_LIGHT = colors.HexColor('#F5EDD6')
    INK = colors.HexColor('#1A1A2E')
    INK_SOFT = colors.HexColor('#4A5568')
    LIGHT = colors.HexColor('#E6F5F3')
    WHITE = colors.white

    c = canvas.Canvas(pdf_path, pagesize=landscape(A4))
    c.setFillColor(WHITE)
    c.rect(0, 0, w, h, fill=1, stroke=0)

    c.setFillColor(TEAL_DARK)
    c.rect(0, 0, 14, h, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(14, 0, 4, h, fill=1, stroke=0)
    c.setFillColor(TEAL_DARK)
    c.rect(w-14, 0, 14, h, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(w-18, 0, 4, h, fill=1, stroke=0)

    c.setFillColor(TEAL_DARK)
    c.rect(0, h-100, w, 100, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(0, h-103, w, 3, fill=1, stroke=0)

    logo_path = 'static/focus_logo.png'
    if os.path.exists(logo_path):
        c.drawImage(ImageReader(logo_path), 28, h-90, width=72, height=72, preserveAspectRatio=True, mask='auto')

    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 26)
    c.drawString(112, h-52, 'FOCUS')
    c.setFillColor(colors.HexColor('#A8D5CC'))
    c.setFont('Helvetica', 9)
    c.drawString(112, h-66, 'LEADERSHIP & DEVELOPPEMENT PERSONNEL')
    c.drawString(112, h-79, 'Burkina Faso')
    c.setFillColor(GOLD)
    c.setFont('Helvetica-Bold', 9)
    c.drawRightString(w-28, h-42, 'ATTESTATION OFFICIELLE')
    c.setFillColor(colors.HexColor('#A8D5CC'))
    c.setFont('Helvetica', 8)
    c.drawRightString(w-28, h-56, 'Programme FOCUS Leadership 2.0')
    c.drawRightString(w-28, h-69, 'Burkina Faso  .  ' + datetime.now().strftime('%Y'))

    c.setFillColor(TEAL)
    c.setFont('Helvetica-Bold', 11)
    c.drawCentredString(w/2, h-124, '---   ATTESTATION DE FORMATION COMPLETE   ---')
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.line(80, h-132, w-80, h-132)

    c.setFillColor(INK_SOFT)
    c.setFont('Helvetica-Oblique', 11)
    c.drawCentredString(w/2, h-152, 'La Coordination FOCUS certifie que')

    c.setFillColor(INK)
    c.setFont('Helvetica-Bold', 34)
    full_name = user['full_name'].upper()
    c.drawCentredString(w/2, h-188, full_name)
    nw = c.stringWidth(full_name, 'Helvetica-Bold', 34)
    c.setStrokeColor(TEAL)
    c.setLineWidth(2)
    c.line(w/2-nw/2-10, h-195, w/2+nw/2+10, h-195)

    if user['establishment']:
        c.setFillColor(INK_SOFT)
        c.setFont('Helvetica', 11)
        c.drawCentredString(w/2, h-212, f"{user['establishment']}  .  {user['city'] or 'Burkina Faso'}")

    c.setFillColor(INK_SOFT)
    c.setFont('Helvetica-Oblique', 11)
    c.drawCentredString(w/2, h-234, "a suivi et valide avec succes l'integralite du")
    c.setFillColor(TEAL_DARK)
    c.setFont('Helvetica-Bold', 13)
    c.drawCentredString(w/2, h-252, 'PROGRAMME DE FORMATION FOCUS LEADERSHIP 2.0')

    box_y = h-310
    c.setFillColor(LIGHT)
    c.roundRect(60, box_y, w-120, 48, 8, fill=1, stroke=0)
    c.setStrokeColor(TEAL)
    c.setLineWidth(1)
    c.roundRect(60, box_y, w-120, 48, 8, fill=0, stroke=1)
    c.setFillColor(TEAL)
    c.setFont('Helvetica-Bold', 9)
    c.drawCentredString(w/2, box_y+36, 'MODULES VALIDES')

    col_w = (w-120) / max(len(certs), 4)
    for i, cert in enumerate(certs):
        cx = 60 + col_w*i + col_w/2
        if i > 0:
            c.setStrokeColor(colors.HexColor('#C8E8E4'))
            c.setLineWidth(0.5)
            c.line(60+col_w*i, box_y+4, 60+col_w*i, box_y+44)
        title = cert['module_title'][:25]
        c.setFillColor(TEAL_DARK)
        c.setFont('Helvetica-Bold', 8)
        c.drawCentredString(cx, box_y+18, title)
        c.setFillColor(GOLD)
        c.setFont('Helvetica-Bold', 9)
        c.drawCentredString(cx, box_y+6, f"Score : {cert['final_score']}%")

    if certs:
        avg = round(sum(cert['final_score'] for cert in certs)/len(certs), 1)
        avg_y = h-365
        c.setFillColor(GOLD_LIGHT)
        c.roundRect(w/2-130, avg_y, 260, 30, 8, fill=1, stroke=0)
        c.setStrokeColor(GOLD)
        c.setLineWidth(1.2)
        c.roundRect(w/2-130, avg_y, 260, 30, 8, fill=0, stroke=1)
        c.setFillColor(TEAL_DARK)
        c.setFont('Helvetica-Bold', 10)
        c.drawCentredString(w/2, avg_y+19, f'Score Moyen : {avg}%   |   Mention : Excellent')
        c.setFont('Helvetica', 8)
        c.setFillColor(INK_SOFT)
        c.drawCentredString(w/2, avg_y+7, f"4 modules completes  .  Valide le {datetime.now().strftime('%d/%m/%Y')}")

    sig_y = h-430
    c.setStrokeColor(colors.HexColor('#E2E8F0'))
    c.setLineWidth(0.8)
    c.line(60, sig_y+36, w-60, sig_y+36)

    s1x = w/4
    c.setStrokeColor(TEAL)
    c.setLineWidth(1)
    c.line(s1x-90, sig_y+28, s1x+90, sig_y+28)
    c.setFillColor(INK_SOFT)
    c.setFont('Helvetica', 8)
    c.drawCentredString(s1x, sig_y+16, 'Le Coordinateur National')
    c.setFillColor(TEAL_DARK)
    c.setFont('Helvetica-Bold', 9)
    c.drawCentredString(s1x, sig_y+4, 'Coordination FOCUS BF')

    s2x = w/2
    c.setStrokeColor(INK_SOFT)
    c.setLineWidth(0.5)
    c.line(s2x-90, sig_y+28, s2x+90, sig_y+28)
    c.setFillColor(INK_SOFT)
    c.setFont('Helvetica', 8)
    c.drawCentredString(s2x, sig_y+16, 'Signature du Laureat(e)')
    c.setFont('Helvetica-Oblique', 8)
    c.drawCentredString(s2x, sig_y+4, user['full_name'])

    s3x = 3*w/4
    c.setStrokeColor(TEAL)
    c.setLineWidth(1)
    c.line(s3x-90, sig_y+28, s3x+90, sig_y+28)
    c.setFillColor(INK_SOFT)
    c.setFont('Helvetica', 8)
    c.drawCentredString(s3x, sig_y+16, 'Date de delivrance')
    c.setFillColor(TEAL_DARK)
    c.setFont('Helvetica-Bold', 10)
    c.drawCentredString(s3x, sig_y+4, datetime.now().strftime('%d / %m / %Y'))

    c.setFillColor(TEAL_DARK)
    c.rect(0, 0, w, 38, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(0, 38, w, 2, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 7)
    pilliers = ['PATRIOTISME', 'INTEGRITE', 'EXCELLENCE', 'SERVICE', 'RELEVE']
    spc = w/(len(pilliers)+1)
    for i, p in enumerate(pilliers):
        c.drawCentredString(spc*(i+1), 25, p)
    c.setFillColor(colors.HexColor('#A8D5CC'))
    c.setFont('Helvetica', 6.5)
    c.drawCentredString(w/2, 10, f'Ref : {attestation_uid}  .  focus-bf.org/verify/attestation/{attestation_uid}')

    seal_x, seal_y = w-72, 72
    c.setFillColor(GOLD)
    c.setStrokeColor(TEAL_DARK)
    c.setLineWidth(2)
    c.circle(seal_x, seal_y, 36, fill=1, stroke=1)
    c.setFillColor(TEAL_DARK)
    c.circle(seal_x, seal_y, 28, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.setFont('Helvetica-Bold', 7)
    c.drawCentredString(seal_x, seal_y+8, 'CERTIFIE')
    c.drawCentredString(seal_x, seal_y-2, 'FOCUS')
    c.setFont('Helvetica', 6)
    c.drawCentredString(seal_x, seal_y-12, datetime.now().strftime('%Y') + ' BF')

    c.save()
    return pdf_path
