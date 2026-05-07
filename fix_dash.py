with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '<div class="module-item">',
    '<a href="/modules/{{ item.module.slug }}" style="text-decoration:none;color:inherit;display:flex;align-items:center;gap:16px;padding:14px 0;border-bottom:1px solid var(--border);">'
).replace(
    '</div>\n        {% endfor %}',
    '</a>\n        {% endfor %}'
)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('OK')
