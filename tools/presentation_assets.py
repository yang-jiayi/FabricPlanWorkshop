"""Deterministic, content-addressed image payloads for the standalone guide."""
import base64
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path
from urllib.parse import urlsplit


PACK = Path('assets/presentation/screenshots.zip')
ICON_PACK = Path('assets/presentation/aurora-icons.zip')
SETTINGS = {'format': 'WEBP', 'quality': 68, 'method': 6}


def screenshot_sources(root):
    sources = []
    for path in sorted((root / 'labs').glob('*.md')):
        for target in re.findall(r'!\[[^\]\n]*\]\(([^)\s]+)', path.read_text(encoding='utf-8')):
            if urlsplit(target).scheme or urlsplit(target).netloc:
                raise ValueError(f'Offline guide cannot load a remote image: {target}')
            resolved = (path.parent / target).resolve().relative_to(root.resolve())
            if resolved not in sources:
                sources.append(resolved)
    return sources


def encode_pack(root):
    from PIL import Image

    manifest = {'settings': SETTINGS, 'images': {}}
    destination = root / PACK
    with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_STORED) as archive:
        for source in screenshot_sources(root):
            raw = (root / source).read_bytes()
            key = hashlib.sha256(raw).hexdigest()
            with Image.open(io.BytesIO(raw)) as image:
                output = io.BytesIO()
                image.save(output, **SETTINGS)
                payload = output.getvalue()
                width, height = image.size
            name = key + '.webp'
            if name not in archive.namelist():
                archive.writestr(zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0)), payload)
            manifest['images'][source.as_posix()] = {
                'source_sha256': key, 'payload_sha256': hashlib.sha256(payload).hexdigest(),
                'width': width, 'height': height,
            }
        archive.writestr(zipfile.ZipInfo('manifest.json', (2026, 1, 1, 0, 0, 0)),
                         json.dumps(manifest, ensure_ascii=False, sort_keys=True))
    return manifest


def read_pack(root):
    payloads = {}
    with zipfile.ZipFile(root / PACK) as archive:
        manifest = json.loads(archive.read('manifest.json'))
        if manifest['settings'] != SETTINGS:
            raise ValueError('Image settings changed; rebuild with --encode-images')
        for source in screenshot_sources(root):
            entry = manifest['images'].get(source.as_posix())
            digest = hashlib.sha256((root / source).read_bytes()).hexdigest()
            if not entry or digest != entry['source_sha256']:
                raise ValueError(f'Screenshot changed: {source}; rebuild with --encode-images')
            key = entry['source_sha256']
            if key not in payloads:
                raw = archive.read(key + '.webp')
                if hashlib.sha256(raw).hexdigest() != entry['payload_sha256']:
                    raise ValueError(f'Corrupt image payload: {source}')
                payloads[key] = 'data:image/webp;base64,' + base64.b64encode(raw).decode('ascii')
        expected = {path.as_posix() for path in screenshot_sources(root)}
        if set(manifest['images']) != expected:
            raise ValueError('Screenshot inventory changed; rebuild with --encode-images')
    return manifest['images'], payloads


def data_uri(path):
    mime = {
        '.svg': 'image/svg+xml', '.png': 'image/png', '.csv': 'text/csv;charset=utf-8',
        '.jpg': 'image/jpeg', '.webp': 'image/webp',
    }[path.suffix.lower()]
    raw = (path.read_text(encoding='utf-8').encode('utf-8')
           if path.suffix.lower() == '.csv' else path.read_bytes())
    return f'data:{mime};base64,' + base64.b64encode(raw).decode('ascii')


def read_icon_pack(root):
    icons = {}
    sources = set()
    with zipfile.ZipFile(root / ICON_PACK) as archive:
        manifest = json.loads(archive.read('manifest.json'))
        for key, entry in manifest.items():
            source = Path(entry['source'])
            if source.parent != Path('assets/brand') or source.suffix != '.svg':
                raise ValueError(f'Invalid icon source: {source}')
            raw = (root / source).read_bytes()
            if hashlib.sha256(raw).hexdigest() != entry['source_sha256']:
                raise ValueError(f'Icon source changed: {source}')
            payload = archive.read(entry['file'])
            if hashlib.sha256(payload).hexdigest() != entry['payload_sha256']:
                raise ValueError(f'Corrupt icon payload: {source}')
            width = entry['width']
            if key != f'{source.name}:{width}':
                raise ValueError(f'Invalid icon entry: {key}')
            svg = 'data:image/svg+xml;base64,' + base64.b64encode(raw).decode('ascii')
            icons[(svg, width)] = 'data:image/webp;base64,' + base64.b64encode(payload).decode('ascii')
            sources.add(source)
    return icons, sources
