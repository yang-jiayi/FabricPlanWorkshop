#!/usr/bin/env python3
"""Check public text and screenshot references for private or stale material."""
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    '.cfg', '.csv', '.dax', '.html', '.ini', '.json', '.md', '.ps1',
    '.py', '.sh', '.sql', '.toml', '.ts', '.txt', '.xml', '.yaml', '.yml',
}
IMAGE_SUFFIXES = {'.gif', '.jpeg', '.jpg', '.png', '.svg', '.webp'}
SKIP_DIRECTORIES = {'.git', '__pycache__', '.venv', 'node_modules'}
EMAIL_RE = re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', re.IGNORECASE)
GUID_RE = re.compile(
    r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b',
    re.IGNORECASE,
)
FORBIDDEN_PATHS = (
    re.compile(r'(?i)docs[\\/]+verification'),
    re.compile(
        r'(?i)(?:copilot[-_]resume(?:[-_]prompt)?|resolution[-_]evidence|'
        r'lab\d\d[-_]captures|approved[-_]changes[-_]recheck)\.(?:md|json)'
    ),
)
LOCAL_PATHS = (
    re.compile(r'(?i)\b[A-Z]:\\(?:Users|Documents and Settings)\\[^\s`"<>)]*'),
    re.compile(r'(?i)' + r'%' + r'LOCALAPPDATA' + r'%'),
    re.compile(r'(?i)FabricWorkshop' + r'Verify'),
)
DEBUG_PORTS = (
    re.compile(r'(?i)\b(?:localhost|127\.0\.0\.1):\d{2,5}\b'),
    re.compile(r'(?i)--remote-debugging-port(?:=|\s+)\d{2,5}\b'),
)
FABRIC_TENANT_URL = re.compile(
    r'(?i)https?://app\.fabric\.microsoft\.com/[^\s<>"\']*?'
    r'(?:groups|workspaces|items)/'
    r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
)
SECRET_PATTERNS = (
    ('JWT-like token', re.compile(
        r'\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b'
    )),
    ('storage account key', re.compile(
        r'(?i)\bAccountKey\s*=\s*[A-Za-z0-9+/=]{20,}'
    )),
    ('SAS signature', re.compile(r'(?i)(?:[?&]|\b)sig=[A-Za-z0-9%/_+-]{12,}')),
    ('bearer token', re.compile(r'(?i)\bBearer\s+[A-Za-z0-9._~+/-]{20,}')),
    ('credential assignment', re.compile(
        r'(?i)\b(?:password|passwd|client_secret|access_token)\s*[:=]\s*'
        r'["\']?[^;\s"\'`<>]{8,}'
    )),
)
PROCESS_IMAGE_WORDING = re.compile(
    r'(?i)(?:\brecheck\b|\bverification\b|\bevidence\b|\bcapture\b|'
    r'\bledger\b|\bindependent review\b|\boperation[-_ ]?id\b|'
    r'再確認|検証記録|検証用|証跡|撮影時刻|確認時刻|操作ID|独立レビュー|台帳)'
)
ALLOWED_EMAIL_DOMAINS = (
    'example.com', 'example.org', 'example.net', 'contoso.com',
    'users.noreply.github.com', 'noreply.github.com',
)
# No repository-specific GUIDs are currently approved as public/sample identifiers.
ALLOWED_PUBLIC_GUIDS = set()


def _is_allowed_email(address):
    domain = address.rsplit('@', 1)[-1].lower()
    return any(domain == allowed or domain.endswith('.' + allowed)
               for allowed in ALLOWED_EMAIL_DOMAINS)


def _text_files(root):
    for path in root.rglob('*'):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in SKIP_DIRECTORIES for part in path.relative_to(root).parts):
            continue
        yield path


def _inspect_text(relative, content):
    issues = []
    for pattern in FORBIDDEN_PATHS:
        if pattern.search(relative) or pattern.search(content):
            issues.append(f'{relative}: removed verification or handoff reference')
            break
    for pattern in LOCAL_PATHS:
        if pattern.search(content):
            issues.append(f'{relative}: local Windows path or profile reference')
            break
    for pattern in DEBUG_PORTS:
        if pattern.search(content):
            issues.append(f'{relative}: local browser debugging port reference')
            break
    if re.search(r'(?i)\bonmicrosoft\.com\b', content):
        issues.append(f'{relative}: Microsoft tenant domain reference')
    if FABRIC_TENANT_URL.search(content):
        issues.append(f'{relative}: tenant-specific Fabric URL')
    for address in EMAIL_RE.findall(content):
        if not _is_allowed_email(address):
            issues.append(f'{relative}: non-example email address')
            break
    for match in GUID_RE.findall(content):
        if match.lower() not in ALLOWED_PUBLIC_GUIDS:
            issues.append(f'{relative}: unclassified GUID')
            break
    for label, pattern in SECRET_PATTERNS:
        if pattern.search(content):
            issues.append(f'{relative}: possible {label}')
    return issues


def _markdown_image_refs(path, content):
    for match in re.finditer(r'!\[([^\]\n]*)\]\(([^)\n]+)\)', content):
        alt = match.group(1).strip()
        destination = match.group(2).strip().split()[0].strip('<>')
        parsed = urlsplit(destination)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        yield alt, (path.parent / unquote(parsed.path)).resolve()

    definitions = {}
    for match in re.finditer(
        r'(?im)^[ \t]*\[([^\]\n]+)\]:[ \t]*(?:<([^>\n]+)>|(\S+))',
        content,
    ):
        label = ' '.join(match.group(1).split()).casefold()
        definitions[label] = match.group(2) or match.group(3)

    references = re.finditer(
        r'!\[([^\]\n]*)\]\[([^\]\n]*)\]|!\[([^\]\n]*)\](?![\[(])',
        content,
    )
    for match in references:
        if match.group(3) is not None:
            alt = match.group(3).strip()
            label = ' '.join(alt.split()).casefold()
        else:
            alt = match.group(1).strip()
            label = ' '.join((match.group(2) or alt).split()).casefold()
        destination = definitions.get(label)
        if not destination:
            continue
        parsed = urlsplit(destination)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        yield alt, (path.parent / unquote(parsed.path)).resolve()


def scan_tree(root=ROOT):
    root = Path(root).resolve()
    issues = []
    markdown_files = sorted(root.rglob('*.md'))
    referenced_screenshots = set()
    for path in _text_files(root):
        relative = path.relative_to(root).as_posix()
        content = path.read_text(encoding='utf-8')
        issues.extend(_inspect_text(relative, content))
        if path.suffix.lower() != '.md':
            continue
        for alt, destination in _markdown_image_refs(path, content):
            relative_image = destination.relative_to(root).as_posix() if destination.is_relative_to(root) else None
            if not destination.is_relative_to(root):
                issues.append(f'{relative}: image reference leaves repository')
                continue
            if not alt:
                issues.append(f'{relative}: image reference has empty alt text')
            if not destination.is_file():
                issues.append(f'{relative}: missing image destination')
                continue
            if relative_image.lower().startswith('assets/screenshots/'):
                referenced_screenshots.add(relative_image.casefold())
            if PROCESS_IMAGE_WORDING.search(alt) or PROCESS_IMAGE_WORDING.search(destination.name):
                issues.append(f'{relative}: process wording in image alt text or file name')

    screenshot_root = root / 'assets' / 'screenshots'
    if screenshot_root.is_dir():
        for path in screenshot_root.rglob('*'):
            if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
                relative_image = path.relative_to(root).as_posix().casefold()
                if relative_image not in referenced_screenshots:
                    issues.append(f'{relative_image}: unreferenced screenshot')
    return markdown_files, issues


def main(root=ROOT):
    markdown_files, issues = scan_tree(root)
    if issues:
        print('\n'.join(issues))
        raise SystemExit(1)
    print(f'PASS: public hygiene checked across {len(markdown_files)} Markdown files; '
          'private patterns, image references, and screenshot usage are clean.')


if __name__ == '__main__':
    main()
