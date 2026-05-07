with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace(
    'from database.db import (',
    'from database.db import (\n    get_all_badges,'
)
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('OK')
