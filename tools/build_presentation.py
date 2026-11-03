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
    'ラボ一覧', '開催と利用上の注意', '原典とライセンス',
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
    }.get(term['term'], term['term'])


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
                return '#en-welcome' if language == 'en' else '#welcome'
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
    for slide in all_slides:
        apply_alerts(slide.tokens, language)
        body = md.renderer.render(slide.tokens, md.options, {'source': slide.source})
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
    assets = [
        UI_ROOT / 'shell.html', UI_ROOT / 'workshop.css', UI_ROOT / 'workshop.js',
        UI_ROOT / 'index-terms.json',
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
