with open('load_all_courses.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '""" Ceci est un commentaire\n    sur plusieurs lignes """',
    "'commentaire sur plusieurs lignes'"
)

content = content.replace(
    'multilignes = """Ceci est\nune chaine\nsur plusieurs lignes"""',
    "multilignes = 'Ceci est une chaine sur plusieurs lignes'"
)

with open('load_all_courses.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('OK')
