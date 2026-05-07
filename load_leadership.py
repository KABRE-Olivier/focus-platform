import sqlite3
conn = sqlite3.connect('focus_platform.db')
cursor = conn.cursor()
cursor.execute("SELECT id FROM modules WHERE slug='leadership'")
mid = cursor.fetchone()[0]
cursor.execute('DELETE FROM quiz_questions WHERE lesson_id IN (SELECT id FROM lessons WHERE module_id=?)', (mid,))
cursor.execute('DELETE FROM lessons WHERE module_id=?', (mid,))
lessons = [
    (mid, 'Chapitre 1 : Quest-ce que FOCUS ?', 'FOCUS est un mouvement de leadership ne au Burkina Faso.\n\nVISION : Institutionnaliser le leadership transformationnel pour un impact national.\n\nMISSION : Former des leaders integres, competents et au service de leur communaute.\n\nMODELE : Coordination Nationale + Cellules Etablissements + Ecosysteme Digital.', 'text', None, 1, 20),
    (mid, 'Chapitre 2 : Les 5 Valeurs', '1. PATRIOTISME : Agir pour le bien collectif.\n2. INTEGRITE : Etre honnete meme quand cest difficile.\n3. EXCELLENCE : Viser le sommet chaque jour.\n4. SERVICE : Diriger pour servir, pas pour dominer.\n5. RELEVE : Former son successeur avant de partir.', 'text', None, 2, 20),
    (mid, 'Chapitre 3 : Les 4 Piliers de Bass', 'PILIER 1 - INFLUENCE IDEALISEE : Le leader est un modele moral.\nPILIER 2 - MOTIVATION INSPIRANTE : Le leader donne du sens, pas des ordres.\nPILIER 3 - STIMULATION INTELLECTUELLE : Le leader challenge ses pairs a innover.\nPILIER 4 - CONSIDERATION INDIVIDUELLE : Le leader accompagne chaque membre selon ses besoins.', 'text', None, 3, 25),
    (mid, 'Chapitre 4 : La Structure FOCUS', 'COORDINATION NATIONALE : Garantit la vision et supervise les cellules.\n\nCELLULES ETABLISSEMENTS (3 poles) :\n- Pole Academique : tutorat et entraide\n- Pole Citoyen : actions de terrain\n- Pole Bien-etre : ecoute et sante mentale\n\nPERENNITE : Chaque responsable forme son adjoint avant de partir.', 'text', None, 4, 20),
    (mid, 'Chapitre 5 : Devenir Leader FOCUS', 'LA BOUSSOLE MORALE DU LEADER :\n1. Mes actions servent-elles ma communaute ?\n2. Suis-je coherent entre paroles et actes ?\n3. Est-ce que j aide quelquun a grandir aujourd hui ?\n\nCHARTE : Incarner les 5 valeurs, former un autre leader, contribuer a ta cellule.', 'text', None, 5, 20),
    (mid, 'Quiz Final - Leadership FOCUS', '', 'quiz', None, 6, 15),
]
cursor.executemany('INSERT INTO lessons (module_id, title, content, lesson_type, video_url, order_index, duration_min) VALUES (?,?,?,?,?,?,?)', lessons)
cursor.execute("SELECT id FROM lessons WHERE module_id=? AND lesson_type='quiz'", (mid,))
qid = cursor.fetchone()[0]
questions = [
    (qid, 'Quelle est la vision de FOCUS ?', 'Former des athletes', 'Institutionnaliser le leadership transformationnel au Burkina Faso', 'Creer une ONG', 'Developper le sport', 'b', 'La vision est d institutionnaliser le leadership transformationnel pour un impact national.', 10, 1),
    (qid, 'Combien de valeurs a FOCUS ?', '3', '4', '5', '6', 'c', 'FOCUS a 5 valeurs : Patriotisme, Integrite, Excellence, Service, Releve.', 10, 2),
    (qid, 'Combien de poles a une cellule FOCUS ?', '2', '3', '4', '5', 'b', 'Chaque cellule a 3 poles : Academique, Citoyen et Bien-etre.', 10, 3),
    (qid, 'Quel pilier de Bass donne du sens plutot que des ordres ?', 'Influence Idealisee', 'Motivation Inspirante', 'Stimulation Intellectuelle', 'Consideration Individuelle', 'b', 'La Motivation Inspirante consiste a communiquer une vision qui donne du sens.', 10, 4),
    (qid, 'Que signifie la Releve dans FOCUS ?', 'Recruter des membres', 'Former son successeur avant de partir', 'Organiser des evenements', 'Gerer le budget', 'b', 'La Releve signifie former son adjoint pour assurer la continuite du mouvement.', 10, 5),
]
cursor.executemany('INSERT INTO quiz_questions (lesson_id, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, points, order_index) VALUES (?,?,?,?,?,?,?,?,?,?)', questions)
conn.commit()
conn.close()
print('Module Leadership charge : 5 chapitres + 5 quiz')
