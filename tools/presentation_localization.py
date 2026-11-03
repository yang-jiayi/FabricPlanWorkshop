"""English article sources and strict parity checks for the offline guide."""
import hashlib
import json
import re
from pathlib import Path
from html.parser import HTMLParser
import html


LOCALE_ROOT = Path('assets/presentation/locales/en')
JAPANESE = re.compile(r'[\u3040-\u30ff\u3400-\u9fff]')


def translate_shell(template, translations):
    class Translator(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=False)
            self.output = []

        def translated(self, value):
            key = value.strip()
            if not JAPANESE.search(key):
                return value
            if key not in translations:
                raise ValueError(f'Missing English interface string: {key}')
            return value.replace(key, translations[key], 1)

        def handle_starttag(self, tag, attrs):
            raw = self.get_starttag_text()
            for name, value in attrs:
                if value and JAPANESE.search(value):
                    raw = raw.replace(f'{name}="{html.escape(value, quote=True)}"',
                                      f'{name}="{html.escape(self.translated(value), quote=True)}"')
            self.output.append(raw)

        def handle_startendtag(self, tag, attrs):
            self.handle_starttag(tag, attrs)

        def handle_endtag(self, tag):
            self.output.append(f'</{tag}>')

        def handle_data(self, data):
            self.output.append(self.translated(data))

        def handle_entityref(self, name):
            self.output.append('&' + name + ';')

        def handle_charref(self, name):
            self.output.append('&#' + name + ';')

        def handle_decl(self, decl):
            self.output.append('<!' + decl + '>')

        def handle_comment(self, data):
            self.output.append('<!--' + data + '-->')

    translator = Translator()
    translator.feed(template)
    return ''.join(translator.output)


def source_digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def section_markdown(slide, lines):
    ranges = [token.map for token in slide.tokens if token.map]
    if not ranges:
        return ''
    return '\n'.join(lines[min(pair[0] for pair in ranges):max(pair[1] for pair in ranges)])


def validate_translation(document, source_text, slides, source):
    if document.get('source_sha256') != source_digest(source_text):
        raise ValueError(f'English translation is stale: {source}')
    expected = {slide.id for slide in slides}
    if set(document.get('sections', {})) != expected:
        raise ValueError(f'English section coverage mismatch: {source}')
    if not document.get('title', '').strip():
        raise ValueError(f'English chapter title missing: {source}')
    lines = source_text.splitlines()
    for slide in slides:
        translated = document['sections'][slide.id]
        if not translated.get('title', '').strip() or not translated.get('markdown', '').strip():
            raise ValueError(f'Empty English section: {slide.id}')
        original = section_markdown(slide, lines)
        for marker in ('presentation-instructor-start', 'presentation-instructor-end'):
            if original.count(marker) != translated['markdown'].count(marker):
                raise ValueError(f'English instructor boundary mismatch: {slide.id}')
        original_answers = len(re.findall(r'<summary>\s*解答\s*</summary>', original))
        translated_answers = len(re.findall(r'<summary>\s*Answers\s*</summary>', translated['markdown']))
        if original_answers != translated_answers:
            raise ValueError(f'English answer coverage mismatch: {slide.id}')
        images = re.findall(r'!\[[^\]\n]*\]\(([^)\s]+)', original)
        translated_images = re.findall(r'!\[[^\]\n]*\]\(([^)\s]+)', translated['markdown'])
        if images != translated_images:
            raise ValueError(f'English image order mismatch: {slide.id}')
        # Commands, queries, UI identifiers and expected numeric values are content, not UI copy.
        original_blocks = re.findall(r'```[^\n]*\n(.*?)```', original, re.S)
        translated_blocks = re.findall(r'```[^\n]*\n(.*?)```', translated['markdown'], re.S)
        if len(original_blocks) != len(translated_blocks):
            raise ValueError(f'English code block coverage mismatch: {slide.id}')


def load_translation(root, lab, source_text, slides, source):
    path = root / LOCALE_ROOT / (lab + '.json')
    document = json.loads(path.read_text(encoding='utf-8'))
    validate_translation(document, source_text, slides, source)
    return document
