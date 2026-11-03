import re
import tempfile
import unittest
from contextlib import redirect_stdout
from html.parser import HTMLParser
from io import StringIO
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt

import build_presentation as presentation


class PresentationTree(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.links = []
        self.resources = []
        self.slides = []
        self.images = []
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'a':
            self.links.append(attrs.get('href', ''))
        if tag in ('img', 'script', 'link', 'iframe', 'source'):
            resource = attrs.get('src') or attrs.get('href') or attrs.get('srcset')
            if resource:
                self.resources.append(resource)
        if tag == 'img':
            self.images.append(attrs)
        if tag == 'script':
            self.scripts.append(attrs)
        if tag == 'section' and 'slide' in attrs.get('class', '').split():
            self.slides.append(attrs)


class PresentationBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generated = presentation.build()
        cls.tree = PresentationTree()
        cls.tree.feed(cls.generated)

    def test_committed_html_is_current_and_deterministic(self):
        self.assertEqual(self.generated, presentation.build())
        actual = (presentation.ROOT / presentation.OUTPUT).read_text(encoding='utf-8')
        self.assertEqual(self.generated, actual)

    def test_all_labs_have_unique_deep_links(self):
        self.assertEqual(len(self.tree.ids), len(set(self.tree.ids)))
        self.assertEqual(
            {slide['data-lab'] for slide in self.tree.slides},
            {'overview'} | {f'lab{number:02d}' for number in range(10)},
        )
        for href in self.tree.links:
            if href.startswith('#'):
                with self.subTest(href=href):
                    self.assertIn(unquote(href[1:]), self.tree.ids)

    def test_every_lab_screenshot_is_preserved_in_source_order(self):
        expected = []
        for path in sorted((presentation.ROOT / 'labs').glob('*.md')):
            content = path.read_text(encoding='utf-8')
            expected.extend(re.findall(r'!\[[^\]\n]*\]\(([^)\s]+)', content))
        actual = [
            image['src'] for image in self.tree.images
            if '/screenshots/' in image.get('src', '')
        ]
        self.assertEqual(actual, expected)
        self.assertGreater(len(actual), 0)
        self.assertTrue(all(image.get('alt') for image in self.tree.images
                            if '/screenshots/' in image.get('src', '')))

    def test_all_resources_are_local_and_exist(self):
        for target in self.tree.resources:
            with self.subTest(target=target):
                self.assertFalse(urlsplit(target).scheme)
                self.assertFalse(urlsplit(target).netloc)
                self.assertTrue((presentation.ROOT / presentation.OUTPUT.parent /
                                 unquote(target)).is_file())
        self.assertEqual(len(self.tree.scripts), 1)
        self.assertNotIn('src', self.tree.scripts[0])
        self.assertNotIn('@import', self.generated)
        self.assertNotIn('fetch(', self.generated)
        self.assertNotIn('XMLHttpRequest', self.generated)

    def test_factual_boundaries_and_author_are_visible(self):
        self.assertIn('Jiayi Yang', self.generated)
        self.assertIn('SQLCandidatesFailedFilterError', self.generated)
        self.assertIn('実PlanからのEnd-to-End確認ではありません', self.generated)
        self.assertIn('Microsoftの公式教材 / 承認を示しません', self.generated)
        self.assertIn('Source fingerprint:', self.generated)

    def test_source_edit_changes_the_generated_output(self):
        original = Path.read_text

        def changed(path, *args, **kwargs):
            text = original(path, *args, **kwargs)
            if path.name.startswith('01-') and path.suffix == '.md':
                return text + '\nPresentation synchronization probe.\n'
            return text

        with patch.object(Path, 'read_text', changed):
            updated = presentation.build()
        self.assertNotEqual(updated, self.generated)
        self.assertIn('Presentation synchronization probe.', updated)

    def test_check_exits_nonzero_for_stale_generated_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'docs').mkdir()
            (root / presentation.OUTPUT).write_text('stale', encoding='utf-8')
            with patch.object(presentation, 'ROOT', root), \
                    patch.object(presentation, 'build', return_value='fresh'), \
                    redirect_stdout(StringIO()):
                self.assertEqual(presentation.main(['--check']), 1)

    def test_split_preserves_nested_steps_and_code_fences(self):
        md = MarkdownIt('default')
        text = (
            '# Lab\n\nStart here.\n\n## Step 1\n\n'
            '1. Read this.\n\n   ```sql\n   SELECT 1;\n   ```\n\n'
            '### Inspect\n\nCheck the result.\n\n## Step 2\n\nStop here.\n'
        )
        title, slides, anchors = presentation.split_document(
            md, Path('labs/00-test.md'), text, 'lab00',
        )
        self.assertEqual(title, 'Lab')
        self.assertEqual(len(slides), 4)
        self.assertEqual(slides[2].parent, 'Step 1')
        self.assertEqual(anchors['inspect'], slides[2].id)
        self.assertTrue(any(token.type == 'fence' for token in slides[1].tokens))
        combined = '\n'.join(md.renderer.render(slide.tokens, md.options, {}) for slide in slides)
        self.assertIn('Read this.', combined)
        self.assertIn('SELECT 1;', combined)
        self.assertIn('Check the result.', combined)

    def test_local_target_keeps_relative_routes_inside_repository(self):
        source = Path('labs/01-start.md')
        self.assertEqual(
            presentation.local_target(source, '../data/README.md#data'),
            (Path('data/README.md'), 'data'),
        )
        self.assertEqual(presentation.local_target(source, '#step'), (source, 'step'))
        self.assertIsNone(presentation.local_target(source, 'https://learn.microsoft.com/'))
        with self.assertRaises(ValueError):
            presentation.local_target(source, '../../outside.png')

    def test_remote_images_fail_the_offline_build(self):
        original = Path.read_text

        def changed(path, *args, **kwargs):
            text = original(path, *args, **kwargs)
            if path.name.startswith('01-') and path.suffix == '.md':
                return text + '\n![Remote](https://example.com/image.png)\n'
            return text

        with patch.object(Path, 'read_text', changed):
            with self.assertRaisesRegex(ValueError, 'remote image'):
                presentation.build()


if __name__ == '__main__':
    unittest.main()
