#!/usr/bin/env python3
"""Build the offline HTML guide from the workshop's canonical Markdown."""
import argparse
import hashlib
import html
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt
from presentation_assets import data_uri, encode_pack, read_pack
from presentation_localization import load_translation, section_markdown, translate_shell


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path('docs/workshop-presentation.html')
INSTRUCTOR_OUTPUT = Path('docs/workshop-instructor.html')
FACILITATOR_SOURCE = Path('docs/FACILITATOR-GUIDE.md')
UI_ROOT = Path('assets/presentation')
OVERVIEW_SECTIONS = {
    'このワークショップで学べること', 'Workshopの目的', 'アーキテクチャ',
    'ラボ一覧', '財務会計用語', '開催と利用上の注意', '原典とライセンス',
}
LAB_ICONS = [
    'fabric_48_color.svg', 'semantic_model_48_item.svg', 'planning_48_item.svg',
    'planning_48_item.svg', 'sql_database_48_item.svg', 'semantic_model_48_item.svg',
    'report_48_item.svg', 'sql_database_48_item.svg', 'fabric_48_color.svg',
    'data_agent_48_item.svg',
]
ALERT_LABELS = {
    'NOTE': '補足', 'TIP': 'ヒント', 'IMPORTANT': '重要',
    'WARNING': '注意', 'CAUTION': '警告',
}
REPOSITORY = 'https://github.com/yang-jiayi/FabricPlanWorkshop/blob/main/'
EXCLUSION = re.compile(
    r'<!-- presentation-exclude-start: ([A-Z0-9-]+) -->\s*\n?(.*?)'
    r'<!-- presentation-exclude-end: \1 -->', re.DOTALL,
)


def exclude_unconfirmed(text):
    cleaned = EXCLUSION.sub('', text)
    if 'presentation-exclude-' in cleaned:
        raise ValueError('Unbalanced presentation exclusion markers')
    return cleaned


def edition_markdown(text, edition):
    """Remove instructor content before rendering or constructing the index."""
    marker = re.compile(r'<!-- presentation-instructor-start -->.*?'
                        r'<!-- presentation-instructor-end -->', re.S)
    cleaned = marker.sub('', text)
    if 'presentation-instructor-' in cleaned:
        raise ValueError('Unbalanced instructor content markers')
    if edition == 'instructor':
        return text.replace('<!-- presentation-instructor-start -->', '').replace(
            '<!-- presentation-instructor-end -->', '')
    # Match full details ranges, including nested details, rather than hiding answers.
    stack = []
    ranges = []
    for match in re.finditer(r'</?details\b[^>]*>', cleaned, re.I):
        if not match[0].startswith('</'):
            stack.append(match.start())
        elif stack:
            start = stack.pop()
            content = cleaned[start:match.end()]
            summary = re.match(r'<details\b[^>]*>\s*<summary\b[^>]*>(.*?)</summary>',
                               content, re.S | re.I)
            if summary and re.sub(r'<[^>]*>', '', summary[1]).strip() in ('解答', 'Answers'):
                ranges.append((start, match.end()))
    outer_ranges = [(start, end) for start, end in ranges
                    if not any(other_start < start and end <= other_end
                               for other_start, other_end in ranges)]
    for start, end in sorted(outer_ranges, reverse=True):
        cleaned = cleaned[:start] + cleaned[end:]
    return cleaned


def english_term(term):
    return {
        'SQLデータベース': 'SQL database', 'シナリオ': 'Scenario',
        'セマンティックモデル': 'Semantic model', '書き戻し': 'Writeback', '配賦': 'Allocation',
    }.get(term['term'], term.get('en', term['term']))


def annotate_financial_terms(rendered, entries, language, lab):
    class Annotator(HTMLParser):
        blocked = {'a', 'button', 'code', 'h1', 'h2', 'h3', 'h4', 'kbd',
                   'pre', 'script', 'style', 'summary'}
        void = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                'link', 'meta', 'param', 'source', 'track', 'wbr'}

        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.output = []
            self.blocked_depth = 0
            self.used = set()

        def handle_starttag(self, tag, attrs):
            if tag in self.blocked:
                self.blocked_depth += 1
            self.output.append(self.get_starttag_text())

        def handle_startendtag(self, tag, attrs):
            self.output.append(self.get_starttag_text())

        def handle_endtag(self, tag):
            self.output.append(f'</{tag}>')
            if tag in self.blocked:
                self.blocked_depth = max(0, self.blocked_depth - 1)

        def handle_data(self, data):
            if self.blocked_depth:
                self.output.append(html.escape(data))
                return
            candidates = []
            for entry in entries:
                if entry['id'] in self.used or entry.get('labs') and lab not in entry['labs']:
                    continue
                aliases = list(dict.fromkeys(
                    [part.strip() for part in entry['term'][language].split(' / ')]
                    + entry['aliases'].get(language, [])
                    + entry['aliases'].get('ja' if language == 'en' else 'en', [])
                ))
                for alias in aliases:
                    if entry['id'] == 'fiscal-year' and alias.casefold() == 'fy':
                        pattern = re.compile(r'(?<![A-Za-z0-9])FY(?:\s|-)?\d{2,4}(?![A-Za-z0-9])', re.I)
                    elif re.search(r'[A-Za-z0-9]', alias):
                        pattern = re.compile(
                            r'(?<![A-Za-z0-9])' + re.escape(alias) + r'(?![A-Za-z0-9])',
                            re.I,
                        )
                    else:
                        pattern = re.compile(re.escape(alias), re.I)
                    for match in pattern.finditer(data):
                        if any(re.search(re.escape(prefix) + r'\s*$', data[:match.start()], re.I)
                               for prefix in entry.get('exclude_prefixes', [])):
                            continue
                        candidates.append((match.start(), -len(match[0]), entry, match))
            candidates.sort(key=lambda item: (item[0], item[1]))
            output = []
            cursor = 0
            for start, _, entry, match in candidates:
                if start < cursor or entry['id'] in self.used:
                    continue
                output.append(html.escape(data[cursor:start]))
                description = '用語の説明' if language == 'ja' else 'Term definition'
                contextual = entry.get('contextual_definitions', {}).get(lab, {}).get(language, '')
                full_definition = entry['definition'][language]
                if contextual:
                    full_definition += ' ' + contextual
                output.append(
                    f'<button type="button" class="finance-term" '
                    f'data-finance-term="{html.escape(entry["id"], quote=True)}" '
                    f'aria-haspopup="dialog" aria-controls="term-dialog" '
                    f'aria-label="{html.escape(match[0] + ": " + description, quote=True)}">'
                    f'{html.escape(match[0])}</button>'
                    f'<span class="finance-term-print" aria-hidden="true">'
                    f' ({html.escape(full_definition)})</span>'
                )
                self.used.add(entry['id'])
                cursor = match.end()
            output.append(html.escape(data[cursor:]))
            self.output.append(''.join(output))

    annotator = Annotator()
    annotator.feed(rendered)
    return ''.join(annotator.output), annotator.used


@dataclass
class Slide:
    id: str
    lab: str
    title: str
    parent: str
    source: Path
    tokens: list


def heading_slug(text):
    """Match the heading fragments used by the repository's Markdown links."""
    plain = re.sub(r'<[^>]*>', '', text).lower()
    plain = ''.join(c for c in plain if c in '-_ ' or
                    unicodedata.category(c)[0] in 'LN')
    return plain.replace(' ', '-')


def local_target(source, target):
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc:
        return None
    path = source if not parsed.path else source.parent / unquote(parsed.path)
    parts = []
    for part in path.parts:
        if part == '..':
            if not parts:
                raise ValueError(f'Link leaves repository: {source}: {target}')
            parts.pop()
        elif part != '.':
            parts.append(part)
    return Path(*parts), unquote(parsed.fragment)


def split_document(md, source, text, lab):
    tokens = md.parse(text)
    title = source.stem
    slides = []
    anchors = {}
    seen = {}
    current = []
    parent = ''
    include = lab != 'overview'
    slide_title = 'このLabを始める前に'
    slide_parent = ''

    def flush():
        nonlocal current
        if include and current and any(t.type not in ('hr',) for t in current):
            slides.append(Slide(
                f'{lab}-s{len(slides):03d}', lab, slide_title, slide_parent,
                source, current,
            ))
        current = []

    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token.type == 'heading_open' and token.level == 0 and token.tag in ('h1', 'h2', 'h3'):
            inline = tokens[index + 1]
            text_title = inline.content
            slug = heading_slug(text_title)
            suffix = seen.get(slug, 0)
            seen[slug] = suffix + 1
            slug = f'{slug}-{suffix}' if suffix else slug
            flush()
            if token.tag == 'h1':
                title = text_title
                slide_title = 'このLabを始める前に'
                slide_parent = ''
            else:
                if token.tag == 'h2':
                    parent = text_title
                    include = lab != 'overview' or parent in OVERVIEW_SECTIONS
                slide_title = text_title
                slide_parent = parent if token.tag == 'h3' else ''
            if include:
                anchors[slug] = f'{lab}-s{len(slides):03d}'
            index += 3
            continue
        current.append(token)
        index += 1
    flush()
    return title, slides, anchors


def apply_alerts(tokens, language='ja'):
    for index, token in enumerate(tokens):
        if token.type != 'blockquote_open' or index + 2 >= len(tokens):
            continue
        inline = tokens[index + 2]
        if inline.type != 'inline':
            continue
        match = re.match(r'^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]', inline.content)
        if not match:
            continue
        kind = match.group(1)
        token.attrSet('class', f'callout callout-{kind.lower()}')
        # Keep the source marker recognizable while making it readable offline.
        if inline.children and inline.children[0].type == 'text':
            inline.children[0].content = inline.children[0].content.replace(
                match.group(0), (kind.title() if language == 'en' else ALERT_LABELS[kind]), 1,
            )


def build(root=ROOT, language='ja', _single=False, edition='participant'):
    if edition not in ('participant', 'instructor'):
        raise ValueError(f'Unknown edition: {edition}')
    root = Path(root)
    if not _single:
        japanese = build(root, 'ja', True, edition)
        english = build(root, 'en', True, edition)
        english_sections = re.findall(r'<section class="slide\b.*?</section>', english, re.S)
        def annotate(section, locale):
            identifier = re.search(r'\bid="([^"]+)"', section)[1]
            article = identifier.removeprefix('en-')
            if locale == 'en':
                section = re.sub(r'\b(id|aria-labelledby)="(?!en-)([^"]+)"',
                                 lambda match: f'{match[1]}="en-{match[2]}"', section)
                section = re.sub(r'href="#(?!en-)([^"]+)"', r'href="#en-\1"', section)
            return section.replace('<section ', f'<section lang="{locale}" data-language="{locale}" '
                                   f'data-article="{article}" ', 1).replace(
                                       'class="slide', ('hidden class="slide' if locale == 'en' else 'class="slide'), 1)
        japanese = re.sub(r'<section class="slide\b.*?</section>',
                          lambda match: annotate(match[0], 'ja'), japanese, flags=re.S)
        extra = '\n'.join(annotate(section, 'en') for section in english_sections)
        japanese = japanese.replace('      </div>\n      <nav class="article-navigation"',
                                    extra + '\n      </div>\n      <nav class="article-navigation"', 1)
        chapters = re.search(r'<nav class="chapter-list"[^>]*>(.*?)</nav>', english, re.S)[1]
        def financial_payload(document):
            payload = re.search(
                r'<script type="application/json" id="finance-terms">(.*?)</script>',
                document, re.S,
            )
            if not payload:
                raise ValueError('Financial glossary payload is missing')
            return json.loads(payload[1])
        japanese_terms = financial_payload(japanese)
        english_terms = financial_payload(english)
        finance_terms = {}
        for term_id in sorted(set(japanese_terms) | set(english_terms)):
            ja = japanese_terms.get(term_id, {})
            en = english_terms.get(term_id, {})
            source_labels = {}
            source_urls = {}
            for source in [*ja.get('sources', []), *en.get('sources', [])]:
                source_urls[source['url']] = source
                source_labels.setdefault(source['url'], {})
                source_labels[source['url']].update(
                    {'ja': source.get('label', '')} if source in ja.get('sources', []) else {}
                )
                source_labels[source['url']].update(
                    {'en': source.get('label', '')} if source in en.get('sources', []) else {}
                )
            finance_terms[term_id] = {
                'term': {'ja': ja.get('term', en.get('term', '')),
                         'en': en.get('term', ja.get('term', ''))},
                'definition': {'ja': ja.get('definition', en.get('definition', '')),
                               'en': en.get('definition', ja.get('definition', ''))},
                'contextual_definitions': ja.get(
                    'contextual_definitions', en.get('contextual_definitions', {}),
                ),
                'sources': [
                    {'url': url, **source_labels[url]}
                    for url in source_urls
                ],
            }
        registered_finance_terms = {
            entry['id'] for entry in json.loads(
                (root / UI_ROOT / 'finance-glossary.json').read_text(encoding='utf-8'),
            )['entries']
        }
        if not set(finance_terms).issubset(registered_finance_terms):
            raise ValueError('Rendered finance term is missing from the glossary registry')
        if edition == 'instructor' and set(finance_terms) != registered_finance_terms:
            missing = sorted(registered_finance_terms - set(finance_terms))
            raise ValueError(f'Financial glossary terms do not occur in either language: {missing}')
        japanese = re.sub(
            r'(<script type="application/json" id="finance-terms">).*?(</script>)',
            lambda match: match[1] + json.dumps(
                finance_terms, ensure_ascii=False, separators=(',', ':'),
            ).replace('<', '\\u003c') + match[2],
            japanese, count=1, flags=re.S,
        )
        ui = json.loads((root / UI_ROOT / 'locales/ui-en.json').read_text(encoding='utf-8'))
        screenshot_count = re.search(r'<span>(\d+)枚の操作画像</span>', japanese)[1]
        def ui_placeholders(value):
            return value.replace('@@SCREENSHOT_COUNT@@', screenshot_count).replace(
                '@@SECTION_COUNT@@', str(len(english_sections)))
        ui = {ui_placeholders(key): ui_placeholders(value) for key, value in ui.items()}
        extras = ('<template id="english-chapters">' + chapters + '</template>'
                  '<script type="application/json" id="ui-translations">'
                  + json.dumps(ui, ensure_ascii=False).replace('<', '\\u003c') + '</script>')
        return japanese.replace('<script>(() =>', extras + '<script>(() =>', 1)
    image_manifest, image_payloads = read_pack(root)
    terms = json.loads((root / UI_ROOT / 'index-terms.json').read_text(encoding='utf-8'))
    glossary_source = UI_ROOT / 'finance-glossary.json'
    glossary_entries = json.loads((root / glossary_source).read_text(encoding='utf-8'))['entries']
    if len({entry['id'] for entry in glossary_entries}) != len(glossary_entries):
        raise ValueError('Financial glossary term IDs must be unique')
    for entry in glossary_entries:
        if not entry.get('sources') or not entry.get('definition', {}).get('ja') or not entry.get('definition', {}).get('en'):
            raise ValueError(f'Financial glossary entry lacks a definition or source: {entry["id"]}')
    stable_sections = json.loads((root / UI_ROOT / 'section-ids.json').read_text(encoding='utf-8'))
    md = MarkdownIt('default', {'html': True}).enable(['table', 'strikethrough'])
    sources = [Path('README.md')]
    for number in range(10):
        matches = sorted((root / 'labs').glob(f'{number:02d}-*.md'))
        if len(matches) != 1:
            raise ValueError(f'Lab{number:02d}: expected exactly one Markdown source')
        sources.append(matches[0].relative_to(root))
    if edition == 'instructor':
        sources.append(FACILITATOR_SOURCE)
    all_slides = []
    chapters = []
    links = {}
    screenshot_paths = set()
    for number, source in enumerate(sources):
        lab = 'facilitator' if source == FACILITATOR_SOURCE else ('overview' if number == 0 else f'lab{number - 1:02d}')
        text = (root / source).read_text(encoding='utf-8')
        if lab != 'overview':
            screenshot_paths.update(re.findall(r'!\[[^\]\n]*\]\(([^)\s]+)', text))
        title, slides, anchors = split_document(md, source, exclude_unconfirmed(text), lab)
        original = [entry for entry in stable_sections if entry['lab'] == lab]
        available = {}
        for entry in original:
            available.setdefault(entry['title'], []).append(entry['id'])
        next_id = max((int(entry['id'].rsplit('s', 1)[1]) for entry in original), default=-1) + 1
        remapped = {}
        for slide in slides:
            old_id = slide.id
            matches = available.get(slide.title, [])
            if matches:
                slide.id = matches.pop(0)
            else:
                slide.id = f'{lab}-s{next_id:03d}'
                next_id += 1
            remapped[old_id] = slide.id
        anchors = {anchor: remapped[slide_id] for anchor, slide_id in anchors.items()}
        if language == 'en':
            translated = load_translation(root, lab, exclude_unconfirmed(text), slides, source)
            title = translated['title']
            for slide in slides:
                entry = translated['sections'][slide.id]
                slide.title = entry['title']
                slide.parent = entry.get('parent', '')
                slide.tokens = md.parse(entry['markdown'])
                slide.id = 'en-' + slide.id
        lines = exclude_unconfirmed(text).splitlines()
        for slide in slides:
            # Filter before parsing so answers never enter rendered or indexed content.
            if language == 'en':
                markdown = translated['sections'][slide.id.removeprefix('en-')]['markdown']
            else:
                markdown = section_markdown(slide, lines)
            slide.tokens = md.parse(edition_markdown(markdown, edition))
        if not slides:
            raise ValueError(f'No presentation sections in {source}')
        label = ('Instructor guide' if language == 'en' else '講師ガイド') if lab == 'facilitator' else ('Overview' if lab == 'overview' else f'Lab{number - 1:02d}')
        icon = 'fabric_48_color.svg' if lab in ('overview', 'facilitator') else LAB_ICONS[number - 1]
        chapters.append((lab, label, title, icon, slides))
        all_slides.extend(slides)
        links[(source, '')] = 'welcome' if number == 0 else slides[0].id
        for fragment, slide_id in anchors.items():
            links[(source, fragment)] = slide_id

    def rewrite(target, source, image=False):
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc:
            if image:
                raise ValueError(f'Offline guide cannot load a remote image: {target}')
            if parsed.scheme not in ('http', 'https', 'mailto'):
                raise ValueError(f'Unsupported link scheme: {target}')
            return target
        destination = local_target(source, target)
        path, fragment = destination
        if path in (OUTPUT, INSTRUCTOR_OUTPUT):
            own_output = INSTRUCTOR_OUTPUT if edition == 'instructor' else OUTPUT
            if path == own_output:
                anchor = fragment or 'welcome'
                if anchor.startswith('en-'):
                    anchor = anchor.removeprefix('en-')
                return '#' + ('en-' if language == 'en' else '') + anchor
            return REPOSITORY + path.as_posix()
        if not (root / path).exists():
            raise ValueError(f'Missing local target: {source}: {target}')
        if not image and destination in links:
            identifier = links[destination]
            return '#' + ('en-' if language == 'en' and not identifier.startswith('en-') else '') + identifier
        if image:
            return data_uri(root / path)
        if path.suffix.lower() == '.csv':
            return data_uri(root / path)
        return REPOSITORY + path.as_posix() + (f'#{parsed.fragment}' if fragment else '')

    original_image = md.renderer.rules['image']

    def image_rule(tokens, index, options, env):
        token = tokens[index]
        target = token.attrGet('src')
        destination = local_target(env['source'], target)
        if destination and destination[0].as_posix() in image_manifest:
            path = destination[0].as_posix()
            entry = image_manifest[path]
            token.attrs.pop('src', None)
            token.attrSet('data-image', entry['source_sha256'])
            token.attrSet('data-source', path)
            token.attrSet('width', str(entry['width']))
            token.attrSet('height', str(entry['height']))
        else:
            token.attrSet('src', rewrite(target, env['source'], image=True))
        token.attrSet('loading', 'lazy')
        token.attrSet('decoding', 'async')
        token.attrSet('class', 'step-image')
        rendered = original_image(tokens, index, options, env)
        alt = md.renderer.renderInlineAsText(token.children, options, env)
        caption = html.escape(alt)
        return (
            '<span class="shot-wrap"><button type="button" class="shot" '
            f'aria-label="{"Enlarge screenshot" if language == "en" else "画像を拡大"}: {html.escape(alt, quote=True)}">'
            f'{rendered}<span class="shot-hint" aria-hidden="true">{"Enlarge" if language == "en" else "拡大"} ↗</span>'
            f'</button><span class="shot-caption">{caption}</span></span>'
        )

    def link_rule(tokens, index, options, env):
        token = tokens[index]
        original_href = token.attrGet('href')
        href = rewrite(original_href, env['source'])
        token.attrSet('href', href)
        if href.startswith('data:text/csv'):
            token.attrSet('download', Path(urlsplit(original_href).path).name)
        if urlsplit(href).scheme in ('https', 'http'):
            token.attrSet('target', '_blank')
            token.attrSet('rel', 'noopener noreferrer')
        return md.renderer.renderToken(tokens, index, options, env)

    def html_rule(tokens, index, options, env):
        # The canonical README uses raw HTML only for layout and local icons.
        rendered = tokens[index].content
        return re.sub(
            r'\b(src|href)="([^"]+)"',
            lambda match: f'{match[1]}="{html.escape(rewrite(match[2], env["source"], image=match[1] == "src"), quote=True)}"',
            rendered,
        )

    def fence_rule(tokens, index, options, env):
        token = tokens[index]
        code_language = token.info.strip().split()[0] if token.info.strip() else ''
        if code_language == 'mermaid':
            # Preserve the canonical diagram source, without a remote renderer.
            return (
                '<details class="diagram-source"><summary>'
                + ('Mermaid diagram source / see the canonical Markdown' if language == 'en'
                   else '構成図のMermaidソース / 正本Markdownも参照')
                + '</summary><pre><code>'
                + html.escape(token.content) + '</code></pre></details>\n'
            )
        return (
            '<div class="code-block"><div class="code-label">'
            + html.escape(code_language or 'text')
            + f'<button type="button" class="copy-code">{"Copy" if language == "en" else "コピー"}</button></div>'
            + f'<pre tabindex="0" aria-label="{"Code / scroll horizontally" if language == "en" else "コード / 横スクロール可能"}"><code>' + html.escape(token.content)
            + '</code></pre></div>\n'
        )

    def code_inline_rule(tokens, index, options, env):
        content = tokens[index].content
        if content == 'data/lab09-variance-snapshot-sample.csv':
            path = root / content
            return (f'<a href="{data_uri(path)}" download="{path.name}">'
                    f'<code>{html.escape(content)}</code></a>')
        return '<code>' + html.escape(content) + '</code>'

    md.renderer.rules.update({
        'image': image_rule, 'link_open': link_rule, 'html_block': html_rule,
        'html_inline': html_rule, 'fence': fence_rule, 'code_inline': code_inline_rule,
    })
    rendered_slides = []
    term_locations = {}
    for slide in all_slides:
        apply_alerts(slide.tokens, language)
        body = md.renderer.render(slide.tokens, md.options, {'source': slide.source})
        body, found_financial_terms = annotate_financial_terms(
            body, glossary_entries, language, slide.lab,
        )
        for term_id in found_financial_terms:
            term_locations.setdefault(term_id, []).append(slide)
        code_text = ' '.join(
            child.content
            for token in slide.tokens
            if token.type == 'inline'
            for child in token.children or []
            if child.type == 'code_inline'
        ) + ' ' + ' '.join(token.content for token in slide.tokens if token.type == 'fence')
        for entry in glossary_entries:
            if entry['id'] in found_financial_terms or not entry.get('code_only'):
                continue
            names = [entry['term'][language], *entry['aliases'].get(language, []),
                     *entry['aliases'].get('ja' if language == 'en' else 'en', [])]
            if any(name.casefold() in code_text.casefold() for name in names):
                term_locations.setdefault(entry['id'], []).append(slide)
        content = unicodedata.normalize('NFKC', slide.title + ' ' + ' '.join(
            token.content for token in slide.tokens if token.type == 'inline')).casefold()
        chips = []
        used_icons = set()
        for term in terms:
            icon = term.get('icon')
            if icon and icon not in used_icons and any(
                unicodedata.normalize('NFKC', alias).casefold() in content
                for alias in [term['term'], english_term(term), *term.get('aliases', [])]
            ):
                used_icons.add(icon)
                chips.append(
                    f'<span class="item-chip"><img class="product-icon" width="22" height="22" alt="" '
                    f'src="{data_uri(root / "assets/brand" / icon)}">{html.escape(english_term(term) if language == "en" else term["term"])}</span>'
                )
        item_chips = f'<div class="item-chips" aria-label="{"Fabric products / items" if language == "en" else "Fabricの製品 / アイテム"}">' + ''.join(chips) + '</div>' if chips else ''
        source_link = REPOSITORY + slide.source.as_posix()
        lab_label = ('Instructor guide' if language == 'en' else '講師ガイド') if slide.lab == 'facilitator' else (
            'Overview' if slide.lab == 'overview' else slide.lab.title())
        rendered_slides.append(
            f'<section class="slide" id="{slide.id}" data-lab="{slide.lab}" '
            f'data-title="{html.escape(slide.title, quote=True)}" aria-labelledby="{slide.id}-title">'
            '<header class="slide-heading"><div class="breadcrumb">'
            f'{lab_label} <span> / {html.escape(slide.parent or "Microsoft Fabric Plan Workshop")}</span></div>'
            f'<h1 id="{slide.id}-title" tabindex="-1">{html.escape(slide.title)}</h1>'
            f'<a class="source-link" href="{source_link}" target="_blank" rel="noopener">{"Canonical Markdown (Japanese)" if language == "en" else "正本Markdown"} ↗</a>'
            '</header>' + item_chips + '<div class="prose">' + body + '</div></section>'
        )

    active_glossary = [entry for entry in glossary_entries if entry['id'] in term_locations]
    if not active_glossary:
        raise ValueError('No verified financial glossary terms occur in the rendered articles')
    glossary_id = 'en-glossary-s000' if language == 'en' else 'glossary-s000'
    glossary_slide = Slide(
        glossary_id, 'glossary',
        'Financial glossary' if language == 'en' else '財務会計用語集',
        '', glossary_source, [],
    )
    glossary_sections = []
    for entry in active_glossary:
        term_id = html.escape(entry['id'], quote=True)
        first_use = term_locations[entry['id']][0]
        contextual = ' / '.join(
            value[language] for value in entry.get('contextual_definitions', {}).values()
            if value.get(language)
        )
        source_links = ' / '.join(
            f'<a href="{html.escape(source["url"], quote=True)}" target="_blank" rel="noopener noreferrer">'
            f'{html.escape(source[language])}</a>'
            for source in entry['sources']
        )
        first_label = '本文の初出' if language == 'ja' else 'First use in the articles'
        context_markup = (
            f'<p class="glossary-context">{html.escape(contextual)}</p>' if contextual else ''
        )
        glossary_sections.append(''.join([
            f'<div class="glossary-entry"><h2 id="glossary-term-{term_id}">'
            f'{html.escape(entry["term"][language])}</h2>',
            f'<p>{html.escape(entry["definition"][language])}</p>',
            context_markup,
            f'<p class="glossary-source">{"出典" if language == "ja" else "Sources"}: {source_links}</p>',
            f'<p><a href="#{first_use.id}">{first_label}: {html.escape(first_use.title)}</a></p>',
            '</div>',
        ]))
    glossary_link = REPOSITORY + glossary_source.as_posix()
    rendered_slides.append(
        f'<section class="slide" id="{glossary_id}" data-lab="glossary" '
        f'data-title="{html.escape(glossary_slide.title, quote=True)}" '
        f'aria-labelledby="{glossary_id}-title">'
        '<header class="slide-heading"><div class="breadcrumb">'
        + ('Glossary' if language == 'en' else '用語集')
        + ' <span> / Microsoft Fabric Plan Workshop</span></div>'
        + f'<h1 id="{glossary_id}-title" tabindex="-1">{html.escape(glossary_slide.title)}</h1>'
        + f'<a class="source-link" href="{glossary_link}" target="_blank" rel="noopener">'
        + ('Glossary source' if language == 'en' else '用語データ') + ' ↗</a>'
        + '</header><div class="prose">' + ''.join(glossary_sections) + '</div></section>'
    )
    all_slides.append(glossary_slide)
    chapters.append((
        'glossary', 'Glossary' if language == 'en' else '用語集',
        'Financial glossary' if language == 'en' else '財務会計用語集',
        'fabric_48_color.svg', [glossary_slide],
    ))

    chapter_buttons = []
    toc_cards = []
    for lab, label, title, icon, slides in chapters:
        start = ('en-welcome' if language == 'en' else 'welcome') if lab == 'overview' else slides[0].id
        icon_tag = (
            f'<img src="../assets/brand/{icon}" width="28" height="28" alt="" '
            'class="product-icon">'
        )
        chapter_buttons.append(
            f'<a class="chapter-link" data-chapter="{lab}" href="#{start}">'
            + icon_tag + f'<span><strong>{label}</strong>'
            f'<span>{html.escape(title)}</span></span></a>'
        )
        steps = ''.join(
            f'<li><a href="#{slide.id}">{html.escape(slide.title)}</a></li>'
            for slide in slides
        )
        toc_cards.append(
            f'<article class="toc-card" data-chapter="{lab}"><a class="toc-chapter" href="#{start}">'
            + icon_tag + f'<span>{label}</span></a><h3>{html.escape(title)}</h3>'
            f'<details><summary>{"Choose a procedure" if language == "en" else "手順を選ぶ"} / {len(slides)} sections</summary>'
            f'<ol>{steps}</ol></details></article>'
        )
    index_entries = []
    current_group = None
    for term in sorted(terms, key=lambda item: english_term(item).casefold()) if language == 'en' else terms:
        group = 'A–Z' if language == 'en' else term['group']
        if group != current_group:
            current_group = group
            index_entries.append(f'<h2>{html.escape(current_group)}</h2>')
        aliases = [alias for alias in term.get('aliases', []) if language != 'en' or not re.search(r'[\u3040-\u9fff]', alias)]
        term_title = english_term(term) if language == 'en' else term['term']
        needles = [unicodedata.normalize('NFKC', word).casefold() for word in [term_title, term['term'], *aliases]]
        occurrences = []
        for slide in all_slides:
            if slide.lab == 'glossary':
                continue
            content = ' '.join(t.content for t in slide.tokens if t.type in ('inline', 'fence'))
            haystack = unicodedata.normalize('NFKC', slide.title + ' ' + content).casefold()
            if any(needle in haystack for needle in needles):
                occurrences.append(slide)
        if not occurrences:
            raise ValueError(f'Index term does not occur: {term["term"]}')
        icon = term.get('icon')
        icon_tag = (f'<img class="product-icon" width="28" height="28" alt="" '
                    f'src="{data_uri(root / "assets/brand" / icon)}">' if icon else '')
        entries = ''.join(f'<li><a href="#{slide.id}">{slide.lab.title()} / {html.escape(slide.title)}</a></li>'
                          for slide in occurrences)
        index_entries.append(
            f'<details class="index-entry" data-group="{html.escape(group)}">'
            f'<summary>{icon_tag}<span>{html.escape(term_title)}</span>'
            f'<span class="index-count">{len(occurrences)}</span></summary>'
            f'<p class="index-aliases">{html.escape(" / ".join(aliases))}</p><ul>{entries}</ul></details>'
        )
    for entry in active_glossary:
        display = entry['term'][language]
        group = entry['group']
        if language == 'en':
            group = group.split(' / ')[-1]
        if group != current_group:
            current_group = group
            index_entries.append(f'<h2>{html.escape(current_group)}</h2>')
        aliases = list(dict.fromkeys(
            entry['aliases'].get(language, [])
            + entry['aliases'].get('ja' if language == 'en' else 'en', [])
        ))
        if language == 'en':
            aliases = [alias for alias in aliases if not re.search(r'[\u3040-\u9fff]', alias)]
        locations = term_locations[entry['id']]
        links = ''.join(
            f'<li><a href="#{slide.id}">{slide.lab.title()} / {html.escape(slide.title)}</a></li>'
            for slide in locations
        )
        index_entries.append(
            f'<details class="index-entry finance-index-entry" data-group="{html.escape(group)}">'
            f'<summary><span>{html.escape(display)}</span>'
            f'<span class="index-count">{len(locations)}</span></summary>'
            f'<p class="index-aliases">{html.escape(" / ".join(aliases))}</p>'
            f'<p class="index-definition">{html.escape(entry["definition"][language])}</p>'
            f'<ul>{links}</ul></details>'
        )
    finance_payload = {
        entry['id']: {
            'term': entry['term'][language],
            'definition': entry['definition'][language],
            'contextual_definitions': entry.get('contextual_definitions', {}),
            'sources': [
                {'label': source[language], 'url': source['url']}
                for source in entry['sources']
            ],
        }
        for entry in active_glossary
    }
    assets = [
        UI_ROOT / 'shell.html', UI_ROOT / 'workshop.css', UI_ROOT / 'workshop.js',
        UI_ROOT / 'index-terms.json', glossary_source,
        UI_ROOT / 'section-ids.json',
        Path('tools/build_presentation.py'), Path('requirements-docs.txt'),
        Path('tools/presentation_assets.py'),
        Path('tools/presentation_localization.py'),
        *[path.relative_to(root) for path in (root / UI_ROOT / 'locales').rglob('*.json')],
    ]
    digest = hashlib.sha256()
    for source in sorted([*sources, *assets], key=lambda path: path.as_posix()):
        digest.update(source.as_posix().encode('utf-8'))
        digest.update(b'\0')
        digest.update((root / source).read_text(encoding='utf-8').encode('utf-8'))
    replacements = {
        'STYLES': (root / UI_ROOT / 'workshop.css').read_text(encoding='utf-8'),
        'SCRIPT': (root / UI_ROOT / 'workshop.js').read_text(encoding='utf-8'),
        'SLIDES': '\n'.join(rendered_slides),
        'CHAPTERS': '\n'.join(chapter_buttons),
        'TOC': '\n'.join(toc_cards),
        'DIGEST': digest.hexdigest(),
        'SECTION_COUNT': str(len(all_slides) + 3),
        'SCREENSHOT_COUNT': str(len(screenshot_paths)),
        'INDEX': '\n'.join(index_entries),
        'IMAGE_PAYLOADS': json.dumps(image_payloads, separators=(',', ':')),
        'FINANCE_TERMS': json.dumps(finance_payload, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c'),
        'EDITION': '講師用' if edition == 'instructor' else '参加者用',
    }
    template = (root / UI_ROOT / 'shell.html').read_text(encoding='utf-8')
    template = template.replace('@@EDITION@@', replacements['EDITION'])
    if language == 'en':
        template = translate_shell(template, json.loads(
            (root / UI_ROOT / 'locales/ui-en.json').read_text(encoding='utf-8')))
    rendered = re.sub(r'@@([A-Z_]+)@@', lambda match: replacements[match[1]], template)
    # Templates and navigation use the same original, unmodified icon files.
    rendered = re.sub(
        r'src="\.\./assets/brand/([^"]+)"',
        lambda match: f'src="{data_uri(root / "assets/brand" / match[1])}"', rendered,
    )
    rendered = re.sub(r'href="\.\./([^"]+)"',
                      lambda match: f'href="{REPOSITORY}{match[1]}"', rendered)
    if 'id="image-payloads"' not in rendered:
        rendered = rendered.replace('</body>', '<script type="application/json" id="image-payloads">'
                                    + replacements['IMAGE_PAYLOADS'] + '</script></body>')
    return rendered


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='fail if generated HTML is stale')
    parser.add_argument('--encode-images', action='store_true', help='refresh the committed full-resolution WebP pack')
    args = parser.parse_args(argv)
    if args.encode_images:
        encode_pack(ROOT)
    for edition, output in [('participant', OUTPUT), ('instructor', INSTRUCTOR_OUTPUT)]:
        generated = build(edition=edition)
        destination = ROOT / output
        if args.check:
            if not destination.exists() or destination.read_text(encoding='utf-8') != generated:
                print(f'FAIL: regenerate {output.as_posix()} with python -X utf8 tools/build_presentation.py')
                return 1
            print(f'PASS: {edition} offline presentation matches its sources.')
        else:
            destination.write_text(generated, encoding='utf-8', newline='\n')
            print(f'Generated {output.as_posix()}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
