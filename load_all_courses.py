"""
FOCUS Platform — Chargement Cours Python + Anglais + Systeme Attestation Globale
=================================================================================
Lance avec : py load_all_courses.py
"""

import sqlite3
import os

conn = sqlite3.connect('focus_platform.db')
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

# ═══════════════════════════════════════════════
# MODULE PYTHON
# ═══════════════════════════════════════════════

cursor.execute("SELECT id FROM modules WHERE slug='python'")
mod = cursor.fetchone()
mid_python = mod[0]

cursor.execute("DELETE FROM quiz_questions WHERE lesson_id IN (SELECT id FROM lessons WHERE module_id=?)", (mid_python,))
cursor.execute("DELETE FROM lessons WHERE module_id=?", (mid_python,))

python_lessons = [
    (mid_python, "Chapitre 1 : Decouvrir Python", """Python est un langage de programmation cree en 1989 par Guido Van Rossum. Sa premiere version officielle est sortie en 1991.

POURQUOI PYTHON ?
Python est aujourd'hui l'un des langages les plus utilises au monde. Voici pourquoi :
- Multiplateforme : il fonctionne sur Windows, Mac, Linux, Android et iOS.
- Gratuit et open source : tout le monde peut l'utiliser et le modifier.
- Facile a apprendre : la syntaxe est claire et proche du langage humain.
- Interprete : un programme Python s'execute directement, sans compilation.
- Oriente objet : on peut modeliser des entites du monde reel.
- Tres utilise en data science, intelligence artificielle, developpement web, et automatisation.

Python est actuellement en version 3. La version 2 est obsolete depuis janvier 2020 — ne l'utilisez plus.

COMMENT INSTALLER PYTHON ?
Telecharge Python depuis : www.python.org/downloads/
Dans ce cours, nous utilisons Python 3.11.

PREMIERS PAS
Une fois Python installe, ouvre le terminal et tape : python
Tu verras l'interpreteur Python. Tu peux y ecrire des instructions directement.

Exemple :
print("Bonjour FOCUS !")  # Affiche : Bonjour FOCUS !
age = 20
print("Mon age est", age)  # Affiche : Mon age est 20

Les programmes Python sont enregistres dans des fichiers avec l'extension .py
Pour executer un fichier : python mon_programme.py

LES COMMENTAIRES
Les commentaires expliquent le code. Ils ne sont pas executes.
# Ceci est un commentaire sur une ligne
'commentaire sur plusieurs lignes'

BONNE PRATIQUE : Commenter son code est essentiel pour le relire et le partager.""", "text", None, 1, 25),

    (mid_python, "Chapitre 2 : Variables, Types et Operateurs", """LES VARIABLES
Une variable est un espace memoire qui stocke une valeur. En Python, la declaration et l'initialisation se font en meme temps.

Exemples :
age = 20          # entier (int)
pi = 3.14         # reel (float)
nom = "FOCUS"     # chaine de caracteres (str)
actif = True      # booleen (bool)

Python est a typage dynamique : il devine automatiquement le type.
Pour connaitre le type d'une variable : type(age)  # <class 'int'>

Declaration multiple sur une ligne :
longueur, largeur = 10, 5

LES TYPES DE BASE
- int : nombres entiers (1, 42, -5)
- float : nombres reels (3.14, -0.5)
- str : chaines de caracteres ("Bonjour", 'FOCUS')
- bool : True ou False
- None : valeur vide

CONVERSION DE TYPES
int("42")     # Convertit la chaine "42" en entier 42
float("3.14") # Convertit en reel
str(42)       # Convertit l'entier 42 en chaine "42"

LES OPERATEURS ARITHMETIQUES
+ : addition       5 + 3 = 8
- : soustraction   5 - 3 = 2
* : multiplication  5 * 3 = 15
/ : division        10 / 3 = 3.333...
// : division entiere  10 // 3 = 3
% : modulo (reste)  10 % 3 = 1
** : puissance      2 ** 3 = 8

LES OPERATEURS DE COMPARAISON
== : egal          5 == 5 → True
!= : different     5 != 3 → True
> : superieur      5 > 3  → True
< : inferieur      3 < 5  → True
>= : superieur ou egal
<= : inferieur ou egal

LES OPERATEURS BOOLEENS
and : ET logique   True and False → False
or  : OU logique   True or False  → True
not : NON logique  not True       → False

ENTREES ET SORTIES
print("Resultat :", 5 + 3)   # Affiche : Resultat : 8
nom = input("Ton nom : ")     # Demande une saisie a l'utilisateur
Note : input() retourne toujours une chaine. Pour un nombre :
age = int(input("Ton age : "))""", "text", None, 2, 25),

    (mid_python, "Chapitre 3 : Instructions de Controle", """LES CONDITIONS (if / elif / else)
Les conditions permettent d'executer des instructions selon une situation.

Structure SI (if) :
if condition:
    instruction

Structure SI/SINON (if/else) :
if condition:
    instruction_si_vrai
else:
    instruction_si_faux

Structure SI/SINON SI/SINON (if/elif/else) :
if condition_1:
    instruction_1
elif condition_2:
    instruction_2
elif condition_3:
    instruction_3
else:
    instruction_par_defaut

Exemple concret :
note = int(input("Entrez votre note : "))
if note >= 90:
    print("Excellent !")
elif note >= 70:
    print("Bien")
elif note >= 50:
    print("Passable")
else:
    print("Insuffisant")

ATTENTION : En Python, l'indentation (les espaces au debut de la ligne) est obligatoire. Elle definit les blocs d'instructions.

LA BOUCLE FOR
La boucle for repete un bloc d'instructions un nombre precis de fois.

Syntaxe :
for variable in iterable:
    instruction

Avec range() :
for i in range(5):       # i prend les valeurs 0, 1, 2, 3, 4
    print(i)

for i in range(1, 6):    # i prend les valeurs 1, 2, 3, 4, 5
    print(i)

for i in range(0, 10, 2): # i prend les valeurs 0, 2, 4, 6, 8
    print(i)

Exemple : calculer la somme de 1 a 10
somme = 0
for i in range(1, 11):
    somme = somme + i
print("Somme =", somme)  # Affiche : Somme = 55

LA BOUCLE WHILE
La boucle while repete un bloc tant qu'une condition est vraie.

Syntaxe :
while condition:
    sequence

Exemple :
compteur = 0
while compteur < 5:
    print("Tour", compteur)
    compteur = compteur + 1

ATTENTION : S'assurer que la condition devient fausse a un moment, sinon boucle infinie !""", "text", None, 3, 25),

    (mid_python, "Chapitre 4 : Listes, Tuples et Dictionnaires", """LES LISTES
Une liste est une collection ordonnee d'elements. Les elements peuvent etre de types differents.
Les indices commencent a 0.

Creation :
fruits = ["mangue", "orange", "banane"]
notes = [15, 18, 12, 16]
mixte = ["FOCUS", 2025, True]

Acces aux elements :
print(fruits[0])   # mangue (premier element)
print(fruits[-1])  # banane (dernier element)

Operations courantes :
fruits.append("ananas")     # Ajouter a la fin
len(fruits)                  # Taille de la liste : 4
fruits.remove("orange")      # Supprimer un element
min(notes), max(notes)       # Minimum et maximum
sum(notes)                   # Somme des elements

Parcours d'une liste :
for fruit in fruits:
    print(fruit)

Sous-listes (slicing) :
notes[1:3]   # Elements d'indice 1 et 2 (3 exclu)
notes[:2]    # Les 2 premiers elements

LES TUPLES
Les tuples sont comme des listes mais immuables (non modifiables).
On les cree avec des parentheses.

coordonnees = (48.86, 2.35)   # Latitude, Longitude de Paris
print(coordonnees[0])         # 48.86

Utile pour des donnees qui ne doivent pas changer.

LES DICTIONNAIRES
Un dictionnaire stocke des paires cle-valeur.

etudiant = {
    "nom": "Olivier",
    "prenom": "Kabre",
    "note": 18,
    "ville": "Ouagadougou"
}

Acces :
print(etudiant["nom"])        # Olivier
print(etudiant["note"])       # 18

Modification :
etudiant["note"] = 19         # Modifier une valeur
etudiant["ecole"] = "2iE"     # Ajouter une nouvelle cle

Suppression :
del etudiant["ville"]

Parcours :
for cle in etudiant.keys():
    print(cle, ":", etudiant[cle])

Verification :
"nom" in etudiant             # True

Methodes utiles :
etudiant.keys()    # Toutes les cles
etudiant.values()  # Toutes les valeurs
etudiant.get("age", 0)  # Retourne 0 si "age" n'existe pas""", "text", None, 4, 30),

    (mid_python, "Chapitre 5 : Fonctions et Modules", """LES FONCTIONS
Une fonction est un bloc de code reutilisable qui effectue une tache precise.

Syntaxe :
def nom_de_la_fonction(parametre1, parametre2):
    bloc_d_instructions
    return resultat

Exemple simple :
def saluer(prenom):
    return "Bonjour, " + prenom + " !"

message = saluer("Olivier")
print(message)   # Bonjour, Olivier !

Fonction avec plusieurs parametres :
def calculer_moyenne(note1, note2, note3):
    total = note1 + note2 + note3
    return total / 3

moy = calculer_moyenne(15, 18, 12)
print("Moyenne :", moy)   # Moyenne : 15.0

Parametres avec valeurs par defaut :
def presenter(nom, pays="Burkina Faso"):
    print(nom, "vient du", pays)

presenter("Olivier")           # Olivier vient du Burkina Faso
presenter("Aminata", "Senegal") # Aminata vient du Senegal

Retourner plusieurs valeurs :
def division_complete(a, b):
    quotient = a // b
    reste = a % b
    return quotient, reste

q, r = division_complete(17, 5)
print("Quotient:", q, "Reste:", r)   # Quotient: 3 Reste: 2

VARIABLES LOCALES ET GLOBALES
Variable locale : declaree dans une fonction. N'existe que pendant l'execution de la fonction.
Variable globale : declaree en dehors de toute fonction. Visible partout.

x = 10  # Variable globale

def modifier():
    global x   # Pour modifier la variable globale
    x = 20

modifier()
print(x)  # 20

LES MODULES
Un module est un fichier .py contenant des fonctions reutilisables.

Importer un module complet :
import math
print(math.sqrt(16))    # 4.0
print(math.factorial(5)) # 120

Importer des fonctions specifiques :
from math import sqrt, factorial
print(sqrt(25))     # 5.0

Importer toutes les fonctions :
from math import *

Modules courants :
- math : fonctions mathematiques
- random : nombres aleatoires
- os : interaction avec le systeme
- datetime : gestion des dates

Exemple avec random :
import random
nombre = random.randint(1, 100)   # Nombre aleatoire entre 1 et 100
print(nombre)

Creer son propre module :
Cree un fichier focus_utils.py avec tes fonctions.
Dans un autre fichier : import focus_utils""", "text", None, 5, 30),

    (mid_python, "Chapitre 6 : Chaines de Caracteres", """LES CHAINES DE CARACTERES (str)
Une chaine est une sequence de caracteres entre guillemets simples ou doubles.

creation = "FOCUS Leadership"
creation2 = 'Burkina Faso'
multilignes = 'Ceci est une chaine sur plusieurs lignes'

OPERATIONS DE BASE
Concatenation (assemblage) :
prenom = "Olivier"
nom = "Kabre"
complet = prenom + " " + nom   # Olivier Kabre

Repetition :
trait = "-" * 20   # --------------------

Longueur :
len("FOCUS")   # 5

Acces aux caracteres (indices) :
mot = "Python"
mot[0]    # P (premier caractere)
mot[-1]   # n (dernier caractere)
mot[1:4]  # yth (du 2eme au 4eme inclus)

METHODES IMPORTANTES
Voici les methodes les plus utiles :

"focus".upper()         # FOCUS (majuscules)
"FOCUS".lower()         # focus (minuscules)
"  bonjour  ".strip()   # bonjour (supprimer espaces)
"bonjour".replace("o","0")  # b0nj0ur
"bonjour".find("j")     # 3 (indice de j)
"a;b;c".split(";")      # ["a", "b", "c"]
";".join(["a","b","c"]) # a;b;c
"bonjour".isalpha()     # True (que des lettres)
"12345".isdigit()       # True (que des chiffres)

FORMATAGE DES CHAINES
Methode format() :
nom = "Olivier"
note = 18
message = "Bonjour {}, ta note est {}/20".format(nom, note)
# Bonjour Olivier, ta note est 18/20

f-strings (Python 3.6+) :
message = f"Bonjour {nom}, ta note est {note}/20"
# Meme resultat, plus lisible

PARCOURIR UNE CHAINE
for lettre in "FOCUS":
    print(lettre)   # F, O, C, U, S (une par ligne)

CHAINES IMMUTABLES
Attention : on ne peut pas modifier un caractere directement.
mot = "Python"
mot[0] = "J"  # ERREUR !
Il faut creer une nouvelle chaine :
mot = "J" + mot[1:]   # Jython""", "text", None, 6, 25),

    (mid_python, "Quiz Final — Python pour Leaders", "", "quiz", None, 7, 20),
]

cursor.executemany("""
    INSERT INTO lessons (module_id, title, content, lesson_type, video_url, order_index, duration_min)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", python_lessons)

cursor.execute("SELECT id FROM lessons WHERE module_id=? AND lesson_type='quiz'", (mid_python,))
python_quiz_id = cursor.fetchone()[0]

python_questions = [
    (python_quiz_id, "Quelle fonction Python permet d'afficher un message a l'ecran ?",
     "input()", "display()", "print()", "show()", "c",
     "print() est la fonction standard pour afficher du texte en Python.", 10, 1),

    (python_quiz_id, "Quel est le resultat de 10 // 3 en Python ?",
     "3.33", "3", "1", "4", "b",
     "L'operateur // effectue la division entiere. 10 // 3 = 3 (le reste 1 est ignore).", 10, 2),

    (python_quiz_id, "Comment creer une liste vide en Python ?",
     "liste = {}", "liste = ()", "liste = []", "liste = <> ", "c",
     "Les listes utilisent des crochets []. Les accolades {} sont pour les dictionnaires, les parentheses () pour les tuples.", 10, 3),

    (python_quiz_id, "Quel mot-cle utilise-t-on pour definir une fonction en Python ?",
     "function", "def", "fun", "define", "b",
     "def est le mot-cle Python pour definir une fonction. Exemple : def ma_fonction():", 10, 4),

    (python_quiz_id, "Que retourne len([1, 2, 3, 4, 5]) ?",
     "4", "6", "5", "0", "c",
     "len() retourne le nombre d'elements dans la liste. La liste a 5 elements, donc len() retourne 5.", 10, 5),

    (python_quiz_id, "Quel est le resultat de 'FOCUS'[0] ?",
     "F", "O", "S", "U", "a",
     "Les indices Python commencent a 0. Le premier caractere de 'FOCUS' est 'F' (indice 0).", 10, 6),

    (python_quiz_id, "Comment importer le module math en Python ?",
     "include math", "using math", "import math", "require math", "c",
     "import est le mot-cle Python pour importer un module. Syntaxe : import math", 10, 7),

    (python_quiz_id, "Quelle boucle utiliser quand on connait a l'avance le nombre d'iterations ?",
     "while", "for", "repeat", "loop", "b",
     "La boucle for est ideale quand le nombre d'iterations est connu. La boucle while est pour des conditions inconnues.", 10, 8),
]

cursor.executemany("""
    INSERT INTO quiz_questions
        (lesson_id, question_text, option_a, option_b, option_c, option_d,
         correct_option, explanation, points, order_index)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", python_questions)

print("✅ Module Python charge : 6 chapitres + 8 questions de quiz")

# ═══════════════════════════════════════════════
# MODULE ANGLAIS
# ═══════════════════════════════════════════════

cursor.execute("SELECT id FROM modules WHERE slug='english'")
mod = cursor.fetchone()
mid_english = mod[0]

cursor.execute("DELETE FROM quiz_questions WHERE lesson_id IN (SELECT id FROM lessons WHERE module_id=?)", (mid_english,))
cursor.execute("DELETE FROM lessons WHERE module_id=?", (mid_english,))

english_lessons = [
    (mid_english, "Level A2 — Everyday English for Leaders", """Welcome to your English journey! At level A2, we use simple words and short sentences.

INTRODUCING YOURSELF
My name is... / I am...
I am from Burkina Faso.
I am a student at 2iE.
I am 20 years old.
I study engineering.
I speak French and a little English.

GREETINGS AND BASIC PHRASES
Hello! / Hi! / Good morning! / Good afternoon! / Good evening!
How are you? → I am fine, thank you. / I am good. / Not bad.
What is your name? → My name is Olivier.
Where are you from? → I am from Ouagadougou.
Nice to meet you! / Pleased to meet you!
See you later! / Goodbye! / Bye!

USEFUL VERBS AT A2
I have, I need, I want, I like, I work, I study, I live, I go
Can I...? → Can I ask a question? Can I help you?
I can speak English. / I cannot speak English well yet.

A2 VOCABULARY — FOCUS CONTEXT
Leader = someone who guides a group
Team = a group of people working together
Goal = what you want to achieve
Project = organized work with a specific aim
Meeting = when people come together to talk
Responsibility = a duty you must do
Challenge = a difficult problem to solve
Progress = getting better step by step

SIMPLE SENTENCES PRACTICE
I am a leader in my school.
My team has 5 people.
We have a meeting every week.
My goal is to help my community.
I want to learn English to open more doors.

GRAMMAR FOCUS — Present Simple
Subject + verb (base form)
I study every day.
He works hard.
She speaks two languages.
We meet every Monday.

Negative: I do not (don't) understand.
Question: Do you speak English?

EXERCISE
Complete these sentences:
1. My name ___ Olivier. (is/are)
2. I ___ from Burkina Faso. (am/is)
3. ___ you speak English? (Do/Does)
4. She ___ a leader in her school. (is/are)
Answers: 1-is, 2-am, 3-Do, 4-is""", "text", None, 1, 25),

    (mid_english, "Level B1 — Communicating with Confidence", """At B1, you can talk about familiar topics, describe experiences, and express your opinions.

TALKING ABOUT YOUR EXPERIENCE
I have been a student leader for 2 years.
I have organized several events at my school.
Last year, I created a study group for my classmates.
I worked on a renewable energy project called VoltSafe Guard.
I have learned a lot from this experience.

EXPRESSING OPINIONS
I think that... / In my opinion... / I believe that...
I think that education is the key to development.
In my opinion, young people can change Africa.
I believe that leadership is a skill that can be learned.

I agree with... / I disagree with... / I am not sure about...
I agree with you that teamwork is essential.
I disagree with the idea that leaders are born, not made.

DESCRIBING CHALLENGES AND SOLUTIONS
The main challenge is... / One difficulty is...
The main challenge is motivating people who are tired.
One solution could be... / We could try to...
One solution could be organizing short, energetic meetings.

GRAMMAR FOCUS — Present Perfect vs Past Simple
Present Perfect (has/have + past participle):
I have completed the leadership module. (recently finished)
She has never visited London.
We have worked together for 3 months.

Past Simple (for specific past time):
I completed the module yesterday.
She visited London in 2019.
We worked together last semester.

B1 VOCABULARY — LEADERSHIP AND TECHNOLOGY
Innovation = creating new ideas or solutions
Sustainability = using resources without destroying them for the future
Collaboration = working together toward a common goal
Initiative = taking action without being told
Resilience = recovering quickly from difficulties
Entrepreneurship = starting and running your own business
Digital transformation = using technology to improve processes

PROFESSIONAL SITUATIONS
In a meeting:
"Could you please repeat that?" / "I did not catch that."
"I would like to add something." / "Can I share my point of view?"
"That is a great point." / "I see what you mean."

Sending an email:
Dear Mr./Ms. [Name],
I am writing to... / I would like to inform you that...
Please find attached... / I look forward to hearing from you.
Best regards, / Yours sincerely,

PRACTICE DIALOGUE — Job Interview
Interviewer: Tell me about yourself.
You: I am Olivier Kabre, a student in engineering at 2iE in Burkina Faso. I have been studying for 3 years and I am passionate about renewable energy and leadership development.
Interviewer: What is your greatest strength?
You: I believe my greatest strength is my ability to work in a team and motivate others. I have been the class representative for 2 years and I have organized many events.""", "text", None, 2, 30),

    (mid_english, "Level B2 — Leading and Presenting in English", """At B2, you can express yourself clearly, handle complex topics, and communicate professionally.

PRESENTATIONS AND PUBLIC SPEAKING
Opening your presentation:
"Good morning, everyone. Today, I would like to present..."
"Thank you for being here. The topic I will be discussing is..."
"I have divided my presentation into three parts..."

Signposting (guiding your audience):
"First of all..." / "To begin with..."
"Moving on to..." / "Another important point is..."
"In addition to this..." / "Furthermore..."
"However..." / "On the other hand..."
"To summarize..." / "In conclusion..."
"Any questions? I would be happy to answer them."

PERSUASIVE COMMUNICATION
Building an argument:
"Evidence shows that..." / "Research indicates that..."
"For example..." / "To illustrate this point..."
"This demonstrates that..." / "As a result..."
"The main reason why... is because..."

Conceding and countering:
"While it is true that... it is also important to note that..."
"Although some people argue that... the evidence suggests that..."

NEGOTIATION LANGUAGE
Making proposals:
"I would like to suggest that we..."
"What if we tried a different approach?"
"Perhaps we could find a compromise..."

Responding to proposals:
"That sounds reasonable. However..."
"I can see your point, but I think..."
"I am willing to consider that if..."

GRAMMAR FOCUS — Conditionals
Zero conditional (general truths):
If you study hard, you improve.

First conditional (likely future):
If we work together, we will succeed.
If I get the scholarship, I will study in Europe.

Second conditional (hypothetical):
If I were the president, I would invest more in education.
If we had more resources, we could help more students.

Third conditional (past regret):
If I had studied harder, I would have passed the exam.
If we had planned better, we would not have missed the deadline.

B2 VOCABULARY — AFRICAN DEVELOPMENT AND TECH
Ecosystem = a network of connected elements
Infrastructure = basic systems a society needs (roads, electricity, internet)
Scalability = ability to grow efficiently
Impact investment = money put into projects that help society
Digital inclusion = making technology accessible to everyone
Disruptive innovation = a new approach that changes an entire industry

WRITING PROFESSIONALLY
A compelling proposal:
Context: Clearly describe the problem you want to solve.
Solution: Present your approach with specific details.
Impact: Explain the expected results and who benefits.
Resources: State what you need (budget, time, people).
Conclusion: End with a strong call to action.

FOCUS PRESENTATION TEMPLATE
"Good morning. My name is [Name] and I represent FOCUS, a leadership development movement in Burkina Faso.
Our mission is to train transformational leaders who will drive national development.
We operate through a network of cells in schools and universities across the country.
To date, we have trained [X] young leaders in [X] schools.
Today, I am here to present our vision and explore how we can collaborate.
Thank you for your attention. I welcome your questions."

PRACTICE TASK
Write a 200-word email to a potential partner organization explaining what FOCUS does, why it matters, and what kind of partnership you are looking for.""", "text", None, 3, 35),

    (mid_english, "English Quiz — Levels A2 to B2", "", "quiz", None, 4, 20),
]

cursor.executemany("""
    INSERT INTO lessons (module_id, title, content, lesson_type, video_url, order_index, duration_min)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", english_lessons)

cursor.execute("SELECT id FROM lessons WHERE module_id=? AND lesson_type='quiz'", (mid_english,))
english_quiz_id = cursor.fetchone()[0]

english_questions = [
    (english_quiz_id, "Complete the sentence: 'I ___ from Burkina Faso.'",
     "is", "are", "am", "be", "c",
     "With 'I', we always use 'am'. I am from Burkina Faso.", 10, 1),

    (english_quiz_id, "Which sentence is correct?",
     "She speak English very well.", "She speaks English very well.", "She speaking English very well.", "She is speak English.", "b",
     "In the present simple with he/she/it, we add -s to the verb. She speaks.", 10, 2),

    (english_quiz_id, "What does 'resilience' mean in a leadership context?",
     "Being very strict with your team.", "Giving up when challenges arise.", "Recovering quickly from difficulties and staying strong.", "Refusing to listen to others.", "c",
     "Resilience means the ability to recover quickly from difficulties. It is a key quality of a FOCUS leader.", 10, 3),

    (english_quiz_id, "Which phrase is best to use when you want to add your opinion in a meeting?",
     "Silence is golden.", "I would like to add something.", "That is wrong.", "Stop talking.", "b",
     "In professional settings, 'I would like to add something' is polite and clear.", 10, 4),

    (english_quiz_id, "Complete: 'If we work together, we ___ succeed.'",
     "would", "will", "would have", "had", "b",
     "First conditional (likely future): If + present simple, will + base verb.", 10, 5),

    (english_quiz_id, "What is the correct way to start a professional email?",
     "Hey man,", "Yo!", "Dear Mr. Kabre,", "Sup,", "c",
     "Professional emails start with 'Dear Mr./Ms. [Name],' This is formal and respectful.", 10, 6),

    (english_quiz_id, "What does 'scalability' mean?",
     "The size of a computer screen.", "The ability to grow efficiently as demand increases.", "A type of musical instrument.", "A cooking technique.", "b",
     "Scalability refers to the ability of a system or organization to grow efficiently. Important in tech and leadership.", 10, 7),
]

cursor.executemany("""
    INSERT INTO quiz_questions
        (lesson_id, question_text, option_a, option_b, option_c, option_d,
         correct_option, explanation, points, order_index)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", english_questions)

print("✅ Module Anglais charge : 3 niveaux A2/B1/B2 + 7 questions de quiz")

# ═══════════════════════════════════════════════
# BADGE GLOBAL FOCUS
# ═══════════════════════════════════════════════

cursor.execute("SELECT id FROM badges WHERE slug='focus_certifie'")
if not cursor.fetchone():
    cursor.execute("""
        INSERT INTO badges (slug, name, description, icon, color, trigger_type, trigger_value, points_reward)
        VALUES ('focus_certifie', 'FOCUS Certifie', 'Tous les modules completes. Attestation FOCUS obtenue.', 'star', '#C8A84B', 'manual', 'all_modules', 200)
    """)
    print("✅ Badge FOCUS Certifie cree")

conn.commit()
conn.close()
print("\n🎉 Tous les cours sont charges avec succes !")
print("   Python : 6 chapitres + 8 quiz")
print("   Anglais : 3 niveaux + 7 quiz")
print("   Badge FOCUS Certifie : pret")
