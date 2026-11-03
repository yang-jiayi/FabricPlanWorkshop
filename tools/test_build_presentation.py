import re
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from html.parser import HTMLParser
from html import escape as html_escape
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
            expected.extend((path.parent / target).resolve().relative_to(presentation.ROOT).as_posix()
                            for target in re.findall(r'!\[[^\]\n]*\]\(([^)\s]+)', content))
        actual = [
            image['data-source'] for image in self.tree.images if 'data-image' in image
        ]
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), 578)
        self.assertTrue(all(image.get('alt') for image in self.tree.images
                            if 'data-image' in image))
        self.assertTrue(all(int(image['width']) > 0 and int(image['height']) > 0
                            for image in self.tree.images if 'data-image' in image))

    def test_all_resources_are_local_and_exist(self):
        for target in self.tree.resources:
            with self.subTest(target=target):
                self.assertEqual(urlsplit(target).scheme, 'data')
        self.assertTrue(all('src' not in script for script in self.tree.scripts))
        self.assertNotIn('@import', self.generated)
        self.assertNotIn('fetch(', self.generated)
        self.assertNotIn('XMLHttpRequest', self.generated)

    def test_factual_boundaries_and_author_are_visible(self):
        self.assertIn('Jiayi Yang', self.generated)
        self.assertIn('SQLCandidatesFailedFilterError', self.generated)
        self.assertIn('Microsoftの公式教材 / 承認を示しません', self.generated)
        self.assertIn('Source fingerprint:', self.generated)
        self.assertIn('Diego Diaz', self.generated)
        for term in ('未確認', '未検証', '未実施', '原因未特定', '未実証', '実機未'):
            self.assertNotIn(term, self.generated)

    def test_exclusion_markers_match_agent_list(self):
        marked = []
        for path in [presentation.ROOT / 'README.md', *sorted((presentation.ROOT / 'labs').glob('*.md'))]:
            text = path.read_text(encoding='utf-8')
            starts = re.findall(r'<!-- presentation-exclude-start: ([A-Z0-9-]+) -->', text)
            ends = re.findall(r'<!-- presentation-exclude-end: ([A-Z0-9-]+) -->', text)
            self.assertEqual(starts, ends)
            self.assertEqual(len(presentation.EXCLUSION.findall(text)), len(starts))
            marked.extend(starts)
        listed = re.findall(r'^### ([A-Z0-9-]+)\s*$', (presentation.ROOT / 'docs/UNCONFIRMED-ITEMS-JA.md').read_text(encoding='utf-8'), re.M)
        self.assertGreater(len(marked), 0)
        self.assertEqual(len(marked), len(set(marked)))
        self.assertCountEqual(marked, listed)

    def test_index_terms_have_occurrences_and_aliases(self):
        terms = json.loads((presentation.ROOT / presentation.UI_ROOT / 'index-terms.json').read_text(encoding='utf-8'))
        self.assertGreaterEqual(len(terms), 15)
        for term in terms:
            self.assertIn(html_escape(term['term']), self.generated)
        self.assertIn('class="index-entry"', self.generated)
        self.assertIn('data-group="五十音"', self.generated)

    def test_existing_bookmarks_keep_their_article_titles(self):
        registry = json.loads((presentation.ROOT / presentation.UI_ROOT / 'section-ids.json').read_text(encoding='utf-8'))
        original = {entry['id']: entry['title'] for entry in registry}
        retained = {slide['id']: slide['data-title'] for slide in self.tree.slides}
        for identifier, title in retained.items():
            if identifier in original:
                self.assertEqual(title, original[identifier])
        post_part_two = next(entry for entry in registry if entry['lab'] == 'lab09'
                             and entry['title'].startswith('6. Part 3'))
        self.assertEqual(retained[post_part_two['id']], post_part_two['title'])
        self.assertEqual(retained['lab09-s002'], '確認済みの範囲')

    def test_standalone_size_and_downloads(self):
        self.assertLess(len(self.generated.encode('utf-8')), 50 * 1024 * 1024)
        self.assertTrue(any(target.startswith('data:text/csv') for target in self.tree.links))
        self.assertFalse(any(target.startswith('../') for target in self.tree.links))

    def test_csv_payloads_do_not_depend_on_checkout_line_endings(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'sample.csv'
            path.write_bytes(b'PeriodKey,Value\r\n202601,12.34\r\n')
            windows = presentation.data_uri(path)
            path.write_bytes(b'PeriodKey,Value\n202601,12.34\n')
            self.assertEqual(presentation.data_uri(path), windows)

    def test_exclusions_reject_malformed_markers(self):
        with self.assertRaisesRegex(ValueError, 'Unbalanced'):
            presentation.exclude_unconfirmed('<!-- presentation-exclude-start: TEST -->\nsecret')
        self.assertEqual(presentation.exclude_unconfirmed(
            'before\n<!-- presentation-exclude-start: TEST -->\nsecret\n'
            '<!-- presentation-exclude-end: TEST -->\nafter'), 'before\n\nafter')

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
