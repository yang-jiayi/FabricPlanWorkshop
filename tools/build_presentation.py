#!/usr/bin/env python3
"""Build the offline HTML guide from the workshop's canonical Markdown."""
import argparse
import hashlib
import html
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path('docs/workshop-presentation.html')
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


def apply_alerts(tokens):
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
                match.group(0), ALERT_LABELS[kind], 1,
            )


def build(root=ROOT):
    root = Path(root)
    md = MarkdownIt('default', {'html': True}).enable(['table', 'strikethrough'])
    sources = [Path('README.md')]
    for number in range(10):
        matches = sorted((root / 'labs').glob(f'{number:02d}-*.md'))
        if len(matches) != 1:
            raise ValueError(f'Lab{number:02d}: expected exactly one Markdown source')
        sources.append(matches[0].relative_to(root))
    all_slides = []
    chapters = []
    links = {}
    screenshot_paths = set()
    for number, source in enumerate(sources):
        lab = 'overview' if number == 0 else f'lab{number - 1:02d}'
        text = (root / source).read_text(encoding='utf-8')
        if lab != 'overview':
            screenshot_paths.update(re.findall(r'!\[[^\]\n]*\]\(([^)\s]+)', text))
        title, slides, anchors = split_document(md, source, text, lab)
        if not slides:
            raise ValueError(f'No presentation sections in {source}')
        label = 'Overview' if lab == 'overview' else f'Lab{number - 1:02d}'
        icon = 'fabric_48_color.svg' if number == 0 else LAB_ICONS[number - 1]
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
        if not (root / path).exists():
            raise ValueError(f'Missing local target: {source}: {target}')
        if not image and destination in links:
            return '#' + links[destination]
        # Output is in docs/, so all canonical repository assets are one level up.
        return '../' + path.as_posix() + (f'#{parsed.fragment}' if fragment else '')

    original_image = md.renderer.rules['image']

    def image_rule(tokens, index, options, env):
        token = tokens[index]
        token.attrSet('src', rewrite(token.attrGet('src'), env['source'], image=True))
        token.attrSet('loading', 'lazy')
        token.attrSet('decoding', 'async')
        token.attrSet('class', 'step-image')
        rendered = original_image(tokens, index, options, env)
        alt = md.renderer.renderInlineAsText(token.children, options, env)
        caption = html.escape(alt)
        return (
            '<span class="shot-wrap"><button type="button" class="shot" '
            f'aria-label="画像を拡大: {html.escape(alt, quote=True)}">'
            f'{rendered}<span class="shot-hint" aria-hidden="true">拡大 ↗</span>'
            f'</button><span class="shot-caption">{caption}</span></span>'
        )

    def link_rule(tokens, index, options, env):
        token = tokens[index]
        href = rewrite(token.attrGet('href'), env['source'])
        token.attrSet('href', href)
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
        language = token.info.strip().split()[0] if token.info.strip() else ''
        if language == 'mermaid':
            # Preserve the canonical diagram source, without a remote renderer.
            return (
                '<details class="diagram-source"><summary>構成図のMermaidソース '
                '/ 正本Markdownも参照</summary><pre><code>'
                + html.escape(token.content) + '</code></pre></details>\n'
            )
        return (
            '<div class="code-block"><div class="code-label">'
            + html.escape(language or 'text')
            + '</div><pre tabindex="0" aria-label="コード / 横スクロール可能"><code>' + html.escape(token.content)
            + '</code></pre></div>\n'
        )

    md.renderer.rules.update({
        'image': image_rule, 'link_open': link_rule, 'html_block': html_rule,
        'html_inline': html_rule, 'fence': fence_rule,
    })
    rendered_slides = []
    for slide in all_slides:
        apply_alerts(slide.tokens)
        body = md.renderer.render(slide.tokens, md.options, {'source': slide.source})
        source_link = '../' + slide.source.as_posix()
        lab_label = 'Overview' if slide.lab == 'overview' else slide.lab.title()
        rendered_slides.append(
            f'<section class="slide" id="{slide.id}" data-lab="{slide.lab}" '
            f'data-title="{html.escape(slide.title, quote=True)}" aria-labelledby="{slide.id}-title">'
            '<header class="slide-heading"><div class="eyebrow">'
            f'{lab_label} <span> / {html.escape(slide.parent or "Microsoft Fabric Plan Workshop")}</span></div>'
            f'<h1 id="{slide.id}-title" tabindex="-1">{html.escape(slide.title)}</h1>'
            f'<a class="source-link" href="{source_link}" target="_blank" rel="noopener">正本Markdown ↗</a>'
            '</header><div class="prose">' + body + '</div></section>'
        )

    chapter_buttons = []
    toc_cards = []
    for lab, label, title, icon, slides in chapters:
        start = 'welcome' if lab == 'overview' else slides[0].id
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
            f'<details><summary>手順を選ぶ / {len(slides)} sections</summary>'
            f'<ol>{steps}</ol></details></article>'
        )
    assets = [
        UI_ROOT / 'shell.html', UI_ROOT / 'workshop.css', UI_ROOT / 'workshop.js',
        Path('tools/build_presentation.py'), Path('requirements-docs.txt'),
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
        'SECTION_COUNT': str(len(all_slides) + 1),
        'SCREENSHOT_COUNT': str(len(screenshot_paths)),
    }
    template = (root / UI_ROOT / 'shell.html').read_text(encoding='utf-8')
    return re.sub(r'@@([A-Z_]+)@@', lambda match: replacements[match[1]], template)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='fail if generated HTML is stale')
    args = parser.parse_args(argv)
    generated = build()
    destination = ROOT / OUTPUT
    if args.check:
        if not destination.exists() or destination.read_text(encoding='utf-8') != generated:
            print('FAIL: regenerate with python -X utf8 tools/build_presentation.py')
            return 1
        print('PASS: offline presentation matches canonical Markdown and local UI assets.')
    else:
        destination.write_text(generated, encoding='utf-8', newline='\n')
        print(f'Generated {OUTPUT.as_posix()}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
