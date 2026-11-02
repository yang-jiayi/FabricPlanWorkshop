import tempfile
import unittest
from pathlib import Path

from check_public_hygiene import _inspect_text, scan_tree


class PublicTextHygieneTests(unittest.TestCase):
    def test_allows_example_and_noreply_addresses(self):
        text = 'Contact: facilitator@example.com and build@users.noreply.github.com.'
        self.assertEqual(_inspect_text('README.md', text), [])

    def test_rejects_private_patterns_without_echoing_values(self):
        separator = chr(92)
        fake_path = 'C:' + separator + 'Users' + separator + 'WorkshopUser' + separator + 'file.txt'
        fake_email = 'person' + '@' + 'private.invalid'
        fake_guid = '-'.join(['12345678', '1234', '1234', '1234', '123456789abc'])
        fabric_url = 'https://app.fabric.microsoft.com/groups/' + fake_guid
        token = 'eyJ' + 'a' * 24 + '.' + 'b' * 16 + '.' + 'c' * 16
        text = '\n'.join([
            fake_path,
            fake_email,
            'tenant.' + 'onmicro' + 'soft.com',
            'http://localhost:' + '9222',
            fabric_url,
            'AccountKey=' + 'A' * 24,
            'Bearer ' + 'x' * 24,
            token,
        ])
        issues = _inspect_text('notes.md', text)
        self.assertTrue(any('Windows path' in issue for issue in issues))
        self.assertTrue(any('email address' in issue for issue in issues))
        self.assertTrue(any('tenant domain' in issue for issue in issues))
        self.assertTrue(any('debugging port' in issue for issue in issues))
        self.assertTrue(any('Fabric URL' in issue for issue in issues))
        self.assertTrue(any('unclassified GUID' in issue for issue in issues))
        self.assertTrue(any('storage account key' in issue for issue in issues))
        self.assertTrue(any('bearer token' in issue for issue in issues))
        self.assertTrue(any('JWT-like token' in issue for issue in issues))
        self.assertTrue(all(fake_email not in issue and fake_guid not in issue for issue in issues))


class ScreenshotHygieneTests(unittest.TestCase):
    def test_requires_existing_referenced_images_without_orphans(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            docs = root / 'docs'
            screenshots = root / 'assets' / 'screenshots'
            docs.mkdir()
            screenshots.mkdir(parents=True)
            (screenshots / 'used.png').write_bytes(b'image')
            (screenshots / 'orphan.png').write_bytes(b'image')
            (docs / 'guide.md').write_text(
                '![Useful screen][screen]\n'
                '![Missing screen](../assets/screenshots/missing.png)\n'
                '[screen]: <../assets/screenshots/used.png>\n',
                encoding='utf-8',
            )
            _, issues = scan_tree(root)
            self.assertTrue(any('missing image destination' in issue for issue in issues))
            self.assertTrue(any('unreferenced screenshot' in issue for issue in issues))

    def test_requires_image_alt_text(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            docs = root / 'docs'
            screenshots = root / 'assets' / 'screenshots'
            docs.mkdir()
            screenshots.mkdir(parents=True)
            (screenshots / 'used.png').write_bytes(b'image')
            (docs / 'guide.md').write_text(
                '![](../assets/screenshots/used.png)\n',
                encoding='utf-8',
            )
            _, issues = scan_tree(root)
            self.assertTrue(any('empty alt text' in issue for issue in issues))

    def test_rejects_process_wording_in_alt_text_and_names(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            docs = root / 'docs'
            screenshots = root / 'assets' / 'screenshots'
            docs.mkdir()
            screenshots.mkdir(parents=True)
            (screenshots / 'recheck.png').write_bytes(b'image')
            alt = 'verification screenshot'
            markdown = '!' + '[' + alt + '](../assets/screenshots/recheck.png)\n'
            (docs / 'guide.md').write_text(markdown, encoding='utf-8')
            _, issues = scan_tree(root)
            self.assertTrue(any('process wording' in issue for issue in issues))


if __name__ == '__main__':
    unittest.main()
