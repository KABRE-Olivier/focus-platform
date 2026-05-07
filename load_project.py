import sqlite3
conn = sqlite3.connect('focus_platform.db')
cursor = conn.cursor()
cursor.execute("SELECT id FROM modules WHERE slug='project'")
mid = cursor.fetchone()[0]
cursor.execute('DELETE FROM quiz_questions WHERE lesson_id IN (SELECT id FROM lessons WHERE module_id=?)', (mid,))
cursor.execute('DELETE FROM lessons WHERE module_id=?', (mid,))
lessons = [
    (mid, 'Chapitre 1 : Le Cadrage du Projet', 'Le cadrage repond au POURQUOI et au QUOI avant toute action.\n\nEXPRESSION DU BESOIN : Clarifier les attentes du client avant de commencer.\n\nETUDE DE FAISABILITE :\n- Faisabilite technique : a-t-on les competences ?\n- Faisabilite financiere : le budget est-il suffisant ?\n- Faisabilite temporelle : les delais sont-ils realistes ?\n\nLe QQOQCCP : Qui, Quoi, Ou, Quand, Comment, Combien, Pourquoi.\n\nLA NOTE DE CADRAGE : Document officiel qui valide le lancement. Elle contient les objectifs, le perimetre, les parties prenantes, le budget et les risques.', 'text', None, 1, 20),
    (mid, 'Chapitre 2 : La Planification', 'LE WBS (Work Breakdown Structure) : Decoupe le projet en taches elementaires. Partir du livrable final et decomposer jusqu a des taches de moins de 2 jours.\n\nLE DIAGRAMME DE GANTT : Outil visuel qui montre les taches, leur duree, leur ordre et leurs dependances.\n\nLE CHEMIN CRITIQUE : Sequence de taches la plus longue sans marge. Tout retard sur ces taches retarde tout le projet.\n\nConseils : Concentrez attention et ressources sur le chemin critique.', 'text', None, 2, 20),
    (mid, 'Chapitre 3 : Pilotage et Suivi', 'LES KPI (Key Performance Indicators) :\n- Cout : budget consomme vs prevu\n- Delai : taux d avancement\n- Qualite : taux de defauts\n\nGESTION DES RISQUES :\n1. Identifier les risques\n2. Evaluer : Probabilite x Impact\n3. Planifier : eviter, reduire, transferer ou accepter\n4. Surveiller tout au long du projet\n\nLE COPIL : Reunion periodique avec les decideurs pour presenter l avancement et prendre des decisions strategiques.', 'text', None, 3, 20),
    (mid, 'Chapitre 4 : Gestion Equipe et Communication', 'LA MATRICE RACI :\n- R (Responsible) : qui realise la tache\n- A (Accountable) : qui est responsable du resultat (1 seul)\n- C (Consulted) : qui est consulte avant de decider\n- I (Informed) : qui est informe de l avancement\n\nLE PLAN DE COMMUNICATION : Definit qui recoit quelle information, quand et par quel canal.\n\nGESTION DES CONFLITS : Identifier la cause reelle, ecouter toutes les parties, chercher un compromis gagnant-gagnant.', 'text', None, 4, 20),
    (mid, 'Chapitre 5 : Cloture et Capitalisation', 'LA RECETTE (UAT) : Validation finale par le client. Si conforme, signature du PV de reception.\n\nLE BILAN DE PROJET : Comparaison prevu vs realise sur le budget, les delais et la qualite.\n\nLE REX (Retour d Experience) : Documenter ce qui a bien ou mal fonctionne pour ameliorer les projets futurs.', 'text', None, 5, 20),
    (mid, 'Chapitre 6 : Resolution de Problemes', 'ANALYSE CAUSALE :\n1. Exploration : recenser toutes les causes sans filtre\n2. Approfondissement : isoler la cause racine\n\nDIAGRAMME ISHIKAWA (5M) : Classer les causes par categories (Main-d oeuvre, Methode, Materiel, Milieu, Matiere).\n\nLES 5 POURQUOI : Poser Pourquoi 5 fois pour remonter a la cause profonde.\n\nPOSTURE INGENIEUR :\n1. Action urgence : stabiliser immediatement\n2. Action corrective : eliminer la cause racine\n3. Verification : tester que le probleme ne revient pas', 'text', None, 6, 25),
    (mid, 'Quiz Final - Gestion de Projet', '', 'quiz', None, 7, 15),
]
cursor.executemany('INSERT INTO lessons (module_id, title, content, lesson_type, video_url, order_index, duration_min) VALUES (?,?,?,?,?,?,?)', lessons)
cursor.execute("SELECT id FROM lessons WHERE module_id=? AND lesson_type='quiz'", (mid,))
qid = cursor.fetchone()[0]
questions = [
    (qid, 'Quel document valide officiellement le lancement d un projet ?', 'Le Gantt', 'La Note de Cadrage', 'Le WBS', 'La Matrice RACI', 'b', 'La Note de Cadrage valide le lancement officiel apres accord de toutes les parties.', 10, 1),
    (qid, 'Que signifie le A dans la Matrice RACI ?', 'Acteur qui realise', 'Accountable : responsable du resultat final', 'Analyste', 'Autorise', 'b', 'Le A designe la personne responsable du resultat. Il ne peut y en avoir qu un seul par tache.', 10, 2),
    (qid, "Qu'est-ce que le Chemin Critique ?", 'La tache la plus difficile', 'Le chemin le plus court', 'La sequence de taches sans marge dont le retard impacte tout le projet', 'La liste des risques', 'c', 'Le chemin critique est la sequence avec marge nulle. Tout retard retarde tout le projet.', 10, 3),
    (qid, 'Quel outil decoupe un projet en taches elementaires ?', 'Gantt', '5 Pourquoi', 'WBS', 'QQOQCCP', 'c', 'Le WBS (Work Breakdown Structure) decoupe le projet en livrables puis en taches.', 10, 4),
    (qid, 'Que fait le REX en fin de projet ?', 'Lance un nouveau projet', 'Documente les lecons apprises pour ameliorer les projets futurs', 'Calcule le budget', 'Recrute des membres', 'b', 'Le REX documente ce qui a bien ou mal fonctionne pour capitaliser l experience.', 10, 5),
]
cursor.executemany('INSERT INTO quiz_questions (lesson_id, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, points, order_index) VALUES (?,?,?,?,?,?,?,?,?,?)', questions)
conn.commit()
conn.close()
print('Module Gestion de Projet charge : 6 chapitres + 5 quiz')
