import re

for fname in ['app.py', 'extra_routes.py']:
    with open(fname, 'rb') as f:
        content = f.read()
    content = content.replace(b'\xef\xbb\xbf', b'')
    with open(fname, 'wb') as f:
        f.write(content)
    print(f'{fname} corrige')
