with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()
with open('extra_routes.py', 'r', encoding='utf-8') as f:
    routes = f.read()
content = content.replace('if __name__ == "__main__":', routes + '\nif __name__ == "__main__":')
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('OK - routes ajoutees')
