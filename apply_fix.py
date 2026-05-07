with open('database/db.py', 'r', encoding='utf-8-sig') as f:
    content = f.read()

# Trouver la fin des imports et remplacer le debut
new_top = open('fix_db_top.py', 'r', encoding='utf-8').read()

# Garder tout apres la fonction get_db existante
import re
match = re.search(r'def hash_password', content)
if match:
    rest = content[match.start():]
    new_content = new_top + '\n\n' + rest
    with open('database/db.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('db.py corrige avec succes')
else:
    print('Pattern non trouve')
