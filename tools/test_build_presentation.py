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
        self.language = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'section' and 'slide' in attrs.get('class', '').split():
            self.language = attrs.get('data-language')
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'a':
            self.links.append(attrs.get('href', ''))
        if tag in ('img', 'script', 'link', 'iframe', 'source'):
            resource = attrs.get('src') or attrs.get('href') or attrs.get('srcset')
            if resource:
                self.resources.append(resource)
        if tag == 'img':
            attrs['_language'] = self.language
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
            image['data-source'] for image in self.tree.images
            if 'data-image' in image and image['_language'] == 'ja'
        ]
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), 578)
        self.assertTrue(all(image.get('alt') for image in self.tree.images
                            if 'data-image' in image))
        self.assertTrue(all(int(image['width']) > 0 and int(image['height']) > 0
                            for image in self.tree.images if 'data-image' in image))
        english = [image['data-source'] for image in self.tree.images
                   if 'data-image' in image and image['_language'] == 'en']
        self.assertEqual(english, expected)

    def test_complete_bilingual_articles_share_one_image_registry(self):
        japanese = {slide['data-article'] for slide in self.tree.slides if slide['data-language'] == 'ja'}
        english = {slide['data-article'] for slide in self.tree.slides if slide['data-language'] == 'en'}
        self.assertEqual(japanese, english)
        self.assertGreater(len(english), 200)
        self.assertEqual(self.generated.count('id="image-payloads"'), 1)
        self.assertEqual(self.generated.count('id="language-select"'), 1)
        self.assertIn('id="en-lab09-s002"', self.generated)
        self.assertIn('id="en-index"', self.generated)

    def test_english_fenced_code_and_mermaid_controls_are_localized(self):
        english = '\n'.join(re.findall(
            r'<section lang="en".*?</section>', self.generated, re.S))
        self.assertIn('class="copy-code">Copy</button>', english)
        self.assertIn('aria-label="Code / scroll horizontally"', english)
        self.assertIn('Mermaid diagram source / see the canonical Markdown', english)
        self.assertNotIn('class="copy-code">コピー</button>', english)
        self.assertNotIn('構成図のMermaidソース', english)

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
        for path in [presentation.ROOT / 'README.md', presentation.ROOT / presentation.FACILITATOR_SOURCE,
                     *sorted((presentation.ROOT / 'labs').glob('*.md'))]:
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

    def test_japanese_typography_is_fluid_and_respects_font_preferences(self):
        css = (presentation.ROOT / presentation.UI_ROOT / 'workshop.css').read_text(encoding='utf-8')
        self.assertIn('font-family: "Yu Gothic UI", "Yu Gothic", Meiryo', css)
        self.assertIn('--type-body: clamp(1.0625rem, 1rem + .27vw, 1.25rem)', css)
        self.assertIn('--type-ui: clamp(.9375rem, .875rem + .16vw, 1rem)', css)
        self.assertIn('--type-small: clamp(.875rem, .8125rem + .16vw, .9375rem)', css)
        sizes = re.findall(r'font-size:\s*([^;}]+)', css)
        self.assertTrue(sizes)
        self.assertTrue(all('px' not in size for size in sizes))
        self.assertIn('font-family: Consolas, "Cascadia Code", monospace', css)
        self.assertNotRegex(css, r'(?:^|[;}])\s*html\s*\{[^}]*font-size:')
        script = (presentation.ROOT / presentation.UI_ROOT / 'workshop.js').read_text(encoding='utf-8')
        self.assertNotIn('devicePixelRatio', script)
        self.assertNotIn('screen.width', script)

    def test_motion_is_finite_reduced_and_preserves_icon_geometry(self):
        css = (presentation.ROOT / presentation.UI_ROOT / 'workshop.css').read_text(encoding='utf-8')
        self.assertIn('@keyframes card-shuffle', css)
        self.assertIn('@keyframes hit-pulse', css)
        self.assertIn('@keyframes gradient-arrival', css)
        self.assertIn('@media (prefers-reduced-motion: reduce)', css)
        self.assertIn('@media print {\n  *, *::before, *::after { animation: none !important; transition: none !important; }', css)
        self.assertNotIn('infinite', css)
        self.assertNotRegex(css, r'\b(?:rotate|skew|scaleX|scaleY)\s*\(')
        self.assertNotRegex(css, r'(?:^|[;{])\s*filter\s*:')

    def test_exclusions_reject_malformed_markers(self):
        with self.assertRaisesRegex(ValueError, 'Unbalanced'):
            presentation.exclude_unconfirmed('<!-- presentation-exclude-start: TEST -->\nsecret')
        self.assertEqual(presentation.exclude_unconfirmed(
            'before\n<!-- presentation-exclude-start: TEST -->\nsecret\n'
            '<!-- presentation-exclude-end: TEST -->\nafter'), 'before\n\nafter')

    def test_participant_filters_answers_and_instructor_blocks_before_rendering(self):
        source = ('Question\n<details><summary>Answers</summary>\n'
                  '<details><summary>Reason</summary>private answer</details>\n</details>\n'
                  'Safety warning\n<!-- presentation-instructor-start -->private note'
                  '<!-- presentation-instructor-end -->')
        participant = presentation.edition_markdown(source, 'participant')
        self.assertIn('Question', participant)
        self.assertIn('Safety warning', participant)
        self.assertNotIn('private', participant)
        instructor = presentation.edition_markdown(source, 'instructor')
        self.assertIn('private answer', instructor)
        self.assertIn('private note', instructor)
        for edition in ('participant', 'instructor'):
            with self.assertRaisesRegex(ValueError, 'Unbalanced'):
                presentation.edition_markdown('<!-- presentation-instructor-start -->x', edition)

    def test_source_edit_requires_synchronized_english_translation(self):
        original = Path.read_text

        def changed(path, *args, **kwargs):
            text = original(path, *args, **kwargs)
            if path.name.startswith('01-') and path.suffix == '.md':
                return text + '\nPresentation synchronization probe.\n'
            return text

        with patch.object(Path, 'read_text', changed):
            with self.assertRaisesRegex(ValueError, 'English translation is stale'):
                presentation.build()

    def test_translation_edit_changes_generated_output(self):
        original = Path.read_text

        def changed(path, *args, **kwargs):
            text = original(path, *args, **kwargs)
            if path.name == 'lab01.json':
                content = json.loads(text)
                section = next(iter(content['sections'].values()))
                section['markdown'] += '\nEnglish synchronization probe.\n'
                return json.dumps(content, ensure_ascii=False)
            return text

        with patch.object(Path, 'read_text', changed):
            updated = presentation.build()
        self.assertNotEqual(updated, self.generated)
        self.assertIn('English synchronization probe.', updated)

    def test_check_exits_nonzero_for_stale_generated_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'docs').mkdir()
            (root / presentation.OUTPUT).write_text('stale', encoding='utf-8')
            with patch.object(presentation, 'ROOT', root), \
                    patch.object(presentation, 'build', return_value='fresh'), \
                    redirect_stdout(StringIO()):
                self.assertEqual(presentation.main(['--check']), 1)

    def test_check_rejects_stale_instructor_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'docs').mkdir()
            (root / presentation.OUTPUT).write_text('fresh', encoding='utf-8')
            (root / presentation.INSTRUCTOR_OUTPUT).write_text('stale', encoding='utf-8')
            with patch.object(presentation, 'ROOT', root), \
                    patch.object(presentation, 'build', return_value='fresh'), \
                    redirect_stdout(StringIO()):
                self.assertEqual(presentation.main(['--check']), 1)


class PresentationEditionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.participant = presentation.build()
        cls.instructor = presentation.build(edition='instructor')
        cls.participant_tree = PresentationTree()
        cls.participant_tree.feed(cls.participant)
        cls.instructor_tree = PresentationTree()
        cls.instructor_tree.feed(cls.instructor)

    def test_only_two_current_standalone_outputs(self):
        self.assertEqual({p.name for p in (presentation.ROOT / 'docs').glob('workshop-*.html')},
                         {presentation.OUTPUT.name, presentation.INSTRUCTOR_OUTPUT.name})
        self.assertEqual((presentation.ROOT / presentation.INSTRUCTOR_OUTPUT).read_text(encoding='utf-8'),
                         self.instructor)
        self.assertIn('参加者用', self.participant)
        self.assertIn('Instructor edition', self.instructor)
        for content, tree in [(self.participant, self.participant_tree),
                              (self.instructor, self.instructor_tree)]:
            self.assertLess(len(content.encode('utf-8')), 50 * 1024 * 1024)
            self.assertEqual(len(tree.ids), len(set(tree.ids)))
            self.assertEqual(content.count('id="image-payloads"'), 1)
            self.assertTrue(all(urlsplit(target).scheme == 'data' for target in tree.resources))
            for href in tree.links:
                if href.startswith('#'):
                    self.assertIn(unquote(href[1:]), tree.ids)

    def test_author_credit_and_linkedin_are_in_both_editions(self):
        for content in (self.participant, self.instructor):
            self.assertIn('<meta name="author" content="Jiayi Yang, Swarm Data SE">', content)
            self.assertIn('<strong>Jiayi Yang, Swarm Data SE</strong>', content)
            self.assertIn('href="https://www.linkedin.com/in/yangjiayi/" target="_blank" '
                          'rel="noopener noreferrer">LinkedIn</a>', content)

    def test_answers_are_absent_from_serialized_participant_html(self):
        for lab in range(9):
            document = json.loads((presentation.ROOT / presentation.UI_ROOT /
                                   f'locales/en/lab{lab:02d}.json').read_text(encoding='utf-8'))
            answers = [value['markdown'] for value in document['sections'].values()
                       if '<summary>Answers</summary>' in value['markdown']]
            self.assertEqual(len(answers), 1)
            answer = re.search(r'<summary>Answers</summary>(.*?)</details>', answers[0], re.S)[1]
            first_answer = re.search(r'^1\. (.+)$', answer, re.M)[1]
            # Inspect rendered text, including hidden articles, not just visible UI.
            from html import unescape
            participant_text = unescape(re.sub(r'<[^>]*>', '', self.participant))
            instructor_text = unescape(re.sub(r'<[^>]*>', '', self.instructor))
            plain_answer = unescape(re.sub(r'<[^>]*>', '', MarkdownIt('default').renderInline(first_answer)))
            self.assertNotIn(plain_answer, participant_text)
            self.assertIn(plain_answer, instructor_text)
        self.assertNotIn('<summary>解答</summary>', self.participant)
        self.assertNotIn('<summary>Answers</summary>', self.participant)
        self.assertEqual(self.instructor.count('<summary>解答</summary>'), 9)
        self.assertEqual(self.instructor.count('<summary>Answers</summary>'), 9)

    def test_facilitator_content_and_links_are_instructor_only(self):
        self.assertNotIn('FACILITATOR-GUIDE.md', self.participant)
        self.assertNotIn('data-lab="facilitator"', self.participant)
        self.assertIn('data-lab="facilitator"', self.instructor)
        self.assertIn('当日の進行：合計180分', self.instructor)
        self.assertIn('9,317', self.instructor)
        self.assertNotIn('9,317', self.participant)
        self.assertIn('GEN_DB_010', self.participant)
        self.assertIn('講師に確認してください', self.participant)

    def test_surviving_articles_and_images_are_identical_in_both_editions(self):
        for language in ('ja', 'en'):
            participant = {s['id']: s['data-title'] for s in self.participant_tree.slides
                           if s['data-language'] == language and s['data-article'] != 'welcome'}
            instructor = {s['id']: s['data-title'] for s in self.instructor_tree.slides
                          if s['data-language'] == language and s['data-lab'] != 'facilitator'
                          and s['data-article'] != 'welcome'}
            self.assertEqual(participant, instructor)
            images = lambda tree: [i['data-source'] for i in tree.images if 'data-image' in i
                                   and i['_language'] == language]
            self.assertEqual(images(self.participant_tree), images(self.instructor_tree))
            self.assertEqual(len(images(self.instructor_tree)), 578)
        for term in ('未確認', '未検証', '原因未特定', '未実証'):
            self.assertFalse(term in self.instructor, f'Unconfirmed annotation: {term}')

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
