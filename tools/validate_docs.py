#!/usr/bin/env python3
"""Check Markdown structure, local links, module files, and source attribution."""
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
errors = []
documents = sorted(path for path in ROOT.rglob('*.md') if '.git' not in path.parts)
links_checked = 0

for path in documents:
    content = path.read_text(encoding='utf-8')
    relative = path.relative_to(ROOT)
    if not content.strip():
        errors.append(f'{relative}: empty document')
    fence = None
    prose = []
    for line in content.splitlines():
        marker = re.match(r'^\s*(`{3,}|~{3,})', line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None:
            prose.append(line)
    if fence:
        errors.append(f'{relative}: unclosed code fence')
    body = '\n'.join(prose)
    if body.count('<details>') != body.count('</details>'):
        errors.append(f'{relative}: unbalanced details tags')
    for match in re.finditer(r'!?\[[^\]\n]*\]\(([^\s)]+)(?:\s+"[^"\n]*")?\)', body):
        target = match.group(1).strip('<>')
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        destination = (path.parent / unquote(parsed.path)).resolve()
        links_checked += 1
        if not destination.is_relative_to(ROOT):
            errors.append(f'{relative}: link leaves repository: {target}')
        elif not destination.exists():
            errors.append(f'{relative}: missing link destination: {target}')

for number in range(9):
    matches = list((ROOT / 'labs').glob(f'{number:02d}-*.md'))
    if len(matches) != 1:
        errors.append(f'module {number:02d}: expected one document, found {len(matches)}')

license_path = ROOT / 'LICENSE'
if not license_path.is_file():
    errors.append('LICENSE is missing')
else:
    license_text = license_path.read_text(encoding='utf-8')
    if 'Copyright (c) 2026 Diego Diaz' not in license_text or 'MIT License' not in license_text:
        errors.append('original MIT license attribution missing')

if errors:
    print('\n'.join(errors))
    raise SystemExit(1)
print(f'PASS: {len(documents)} Markdown files, {links_checked} relative links, '
      '9 modules, fences, details, and MIT attribution.')
