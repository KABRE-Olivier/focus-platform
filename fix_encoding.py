with open('app.py', 'r', encoding='utf-8-sig') as f:
    content = f.read()
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('OK')
