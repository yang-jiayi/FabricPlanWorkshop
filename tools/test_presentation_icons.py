import base64
import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from presentation_assets import ICON_PACK, read_icon_pack


class IconPackTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.source = self.root / 'assets/brand/example.svg'
        self.source.parent.mkdir(parents=True)
        self.source.write_bytes(b'<svg/>')
        self.payload = b'encoded webp'
        self.entry = {
            'source': 'assets/brand/example.svg',
            'source_sha256': hashlib.sha256(self.source.read_bytes()).hexdigest(),
            'width': 22,
            'payload_sha256': hashlib.sha256(self.payload).hexdigest(),
            'file': 'example-22.webp',
        }

    def write_pack(self):
        path = self.root / ICON_PACK
        path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(path, 'w') as archive:
            archive.writestr('manifest.json', json.dumps({'example.svg:22': self.entry}))
            archive.writestr('example-22.webp', self.payload)

    def test_reads_matching_source_and_payload(self):
        self.write_pack()
        icons, sources = read_icon_pack(self.root)
        svg = 'data:image/svg+xml;base64,' + base64.b64encode(b'<svg/>').decode()
        webp = 'data:image/webp;base64,' + base64.b64encode(self.payload).decode()
        self.assertEqual(icons, {(svg, 22): webp})
        self.assertEqual(sources, {Path('assets/brand/example.svg')})

    def test_rejects_changed_source(self):
        self.write_pack()
        self.source.write_bytes(b'<svg id="changed"/>')
        with self.assertRaisesRegex(ValueError, 'Icon source changed'):
            read_icon_pack(self.root)

    def test_rejects_corrupt_payload(self):
        self.payload = b'corrupt'
        self.write_pack()
        with self.assertRaisesRegex(ValueError, 'Corrupt icon payload'):
            read_icon_pack(self.root)
