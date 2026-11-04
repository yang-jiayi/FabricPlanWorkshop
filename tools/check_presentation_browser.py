#!/usr/bin/env python3
"""Repeatable file:// quality loop for the standalone workshop (local Edge)."""
import argparse
import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]


def run(output, axe, html_path=ROOT / 'docs/workshop-presentation.html'):
    output.mkdir(parents=True, exist_ok=True)
    report = {'checks': {}, 'console_errors': [], 'network_attempts': [], 'accessibility': {}}

    def check(name, passed):
        report['checks'][name] = bool(passed)
        (output / 'browser-report.json').write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel='msedge')
        page = browser.new_page(viewport={'width': 1440, 'height': 1000},
                                reduced_motion='reduce')
        page.on('pageerror', lambda error: report['console_errors'].append(str(error)))
        page.on('console', lambda message: report['console_errors'].append(message.text)
                if message.type == 'error' else None)
        page.on('request', lambda request: report['network_attempts'].append(request.url)
                if request.url.startswith(('http:', 'https:')) else None)
        started = time.perf_counter()
        page.goto(html_path.resolve().as_uri(), wait_until='load')
        page.wait_for_function("document.documentElement.classList.contains('js')")
        report['load_seconds'] = round(time.perf_counter() - started, 3)
        report['html_bytes'] = html_path.stat().st_size

        def capture(name):
            page.screenshot(path=str(output / (name + '.png')), animations='disabled')

        def audit(name):
            page.add_script_tag(path=str(axe))
            violations = page.evaluate("""async () => (await axe.run(document, {
                runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa']}
            })).violations.map(v => ({id:v.id, impact:v.impact, description:v.description,
                nodes:v.nodes.map(n => ({target:n.target, summary:n.failureSummary}))}))""")
            report['accessibility'][name] = violations
            check('axe_' + name, not any(v['impact'] in ('serious', 'critical') for v in violations))

        capture('after-home')
        audit('home-light')
        check('578_screenshots', page.locator('.slide[data-language="ja"] img[data-image]').count() == 578)
        check('embedded_resources', page.evaluate("""() => [...document.querySelectorAll('img[src]')]
              .every(i => i.getAttribute('src').startsWith('data:'))"""))
        check('links_resolve', page.evaluate("""() => [...document.querySelectorAll('a[href]')].every(a => {
            const h=a.getAttribute('href'); return h.startsWith('#') ?
                !!document.getElementById(decodeURIComponent(h.slice(1))) :
                /^(https?:|mailto:|data:)/.test(h);
        })"""))
        check('zero_unconfirmed_terms', not page.locator('body').inner_text().count('未確認')
              and not page.evaluate("() => /未検証|未実施|原因未特定|未実証/.test(document.body.textContent)"))
        check('under_50_mib', report['html_bytes'] < 50 * 1024 * 1024)
        check('initial_render_under_10_seconds', report['load_seconds'] < 10)
        check('all_payloads_decode_at_original_dimensions', page.evaluate("""async () => {
            const payloads=JSON.parse(document.getElementById('image-payloads').textContent);
            for (const original of document.querySelectorAll('.slide[data-language="ja"] img[data-image]')) {
                const image=new Image(); image.src=payloads[original.dataset.image];
                try { await image.decode(); } catch { return false; }
                if (image.naturalWidth!==Number(original.getAttribute('width')) ||
                    image.naturalHeight!==Number(original.getAttribute('height'))) return false;
                image.src='';
            }
            return true;
        }"""))
        page.locator('#nav-filter').fill('Optimizer')
        check('nav_title_filter', page.locator('.chapter-group:visible').count() == 1)
        page.locator('#nav-filter').fill('')
        toggle = page.locator('.chapter-toggle').first
        was_open = toggle.get_attribute('aria-expanded')
        toggle.click()
        check('nav_expands_collapses', toggle.get_attribute('aria-expanded') != was_open)

        page.evaluate("""location.hash = [...document.querySelectorAll('.slide[data-lab="lab01"]')]
                      .find(s => s.querySelector('.shot')).id""")
        page.wait_for_timeout(200)
        capture('after-lab')
        audit('lab-light')
        check('deep_link_visible', page.locator('.slide:visible').count() == 1)
        for locale in ('ja', 'en'):
            page.locator('#language-select').select_option(locale)
            page.evaluate("""locale => {
                const trigger=document.querySelector(`.slide[data-language="${locale}"] .finance-term`);
                if (!trigger) throw new Error(`No finance term annotation in ${locale}`);
                location.hash=trigger.closest('.slide').id;
            }""", locale)
            page.wait_for_timeout(150)
            trigger = page.locator(f'.slide[data-language="{locale}"]:visible .finance-term').first
            trigger.click()
            check(f'term_dialog_opens_{locale}', page.locator('#term-dialog[open]').count() == 1
                  and page.locator('#term-definition').inner_text().strip() != ''
                  and page.locator('#term-sources a').count() > 0)
            capture(f'after-term-{locale}')
            page.add_script_tag(path=str(axe))
            violations = page.evaluate("""async () => (await axe.run(document, {
                runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa']}
            })).violations.map(v => ({id:v.id, impact:v.impact}))""")
            report['accessibility'][f'term-dialog-{locale}'] = violations
            check(f'term_dialog_axe_{locale}', not violations)
            page.keyboard.press('Escape')
            check(f'term_dialog_escape_focus_{locale}', page.locator('#term-dialog[open]').count() == 0
                  and trigger.evaluate('(element) => document.activeElement === element'))
        page.emulate_media(media='print')
        check('term_definitions_visible_in_print', page.locator('.slide:visible .finance-term-print').count() > 0)
        page.emulate_media(media='screen')
        page.evaluate("""location.hash=[...document.querySelectorAll('.slide')]
                      .find(s=>s.querySelector('.shot')).id""")
        page.wait_for_timeout(150)
        shot = page.locator('.slide:visible .shot').first
        if shot.count():
            shot.click()
            page.wait_for_timeout(150)
            capture('after-lightbox')
            audit('lightbox')
            check('lightbox_opens', page.locator('dialog[open]').count() == 1)
            page.get_by_role('button', name='100%', exact=True).click()
            check('lightbox_pixel_zoom', page.locator('dialog[open] img').evaluate(
                "(i) => i.naturalWidth > 1000 && Math.abs(i.getBoundingClientRect().width-i.naturalWidth)<2"))
            page.locator('#image-plus').click()
            check('lightbox_zoom', page.locator('#zoom-label').inner_text() == '125%')
            page.locator('.image-stage').evaluate('(s) => {s.scrollLeft=80;s.scrollTop=80;}')
            check('lightbox_pan', page.locator('.image-stage').evaluate('(s) => s.scrollLeft>0 || s.scrollTop>0'))
            page.keyboard.press('Escape')
            check('lightbox_closes', page.locator('dialog[open]').count() == 0)
        else:
            check('lightbox_opens', False)

        page.keyboard.press('Control+k')
        search_input = page.locator('dialog[open] input[type="search"]')
        search_input.fill('Ｆｏｒｅｃａｓｔ Gross')
        page.wait_for_timeout(250)
        capture('after-search')
        audit('search')
        check('search_nfkc_and', page.locator('#search-results [role="option"]').count() > 0)
        page.keyboard.press('ArrowDown')
        page.keyboard.press('Enter')
        page.wait_for_timeout(200)
        check('search_keyboard_jump', page.locator('dialog[open]').count() == 0
              and page.locator('.slide:visible mark').count() > 0)

        page.evaluate("location.hash='index'")
        page.wait_for_timeout(200)
        check('search_marks_scoped', page.locator('.slide:visible mark.article-hit').count() == 0)
        capture('after-index')
        audit('index')
        check('index_terms', page.locator('.index-entry:visible').count() >= 15)
        page.locator('.index-entry:visible summary').first.click()
        index_href = page.locator('.index-entry[open] a').first.get_attribute('href')
        page.locator('.index-entry[open] a').first.click()
        check('index_navigation', page.evaluate('location.hash') == index_href)

        page.evaluate("""location.hash=[...document.querySelectorAll('.slide')]
                      .find(s=>s.querySelector('.copy-code')).id""")
        page.wait_for_timeout(150)
        page.locator('.slide:visible .copy-code').first.click()
        page.wait_for_function("""() => /コピーしました|コピーできませんでした/.test(
            document.querySelector('.slide:not([hidden]) .copy-code').textContent)""")
        check('copy_button', page.locator('.slide:visible .copy-code').first.inner_text() == 'コピーしました')
        page.evaluate("""location.hash=[...document.querySelectorAll('.slide')]
                      .find(s=>s.querySelector('a[download*="sample.csv"]')).id""")
        page.wait_for_timeout(150)
        with page.expect_download() as downloaded:
            page.locator('.slide:visible a[download*="sample.csv"]').first.click()
        download = downloaded.value
        check('csv_download_contents', Path(download.path()).read_bytes() ==
              (ROOT / 'data/lab09-variance-snapshot-sample.csv').read_text(encoding='utf-8').encode('utf-8'))

        page.evaluate("location.hash='welcome'")
        page.wait_for_timeout(150)
        theme = page.locator('#theme-toggle')
        for _ in range(3):
            if page.locator('html').get_attribute('data-theme') == 'dark':
                break
            theme.click()
        capture('after-dark')
        audit('home-dark')
        page.evaluate("location.hash = document.querySelector('.slide[data-lab=\"lab09\"]').id")
        page.wait_for_timeout(150)
        audit('lab-dark')
        page.locator('#language-select').select_option('ja')
        page.evaluate("""location.hash=document.querySelector(
            '.slide[data-language="ja"] .finance-term').closest('.slide').id""")
        page.wait_for_timeout(150)
        dark_trigger = page.locator('.slide:visible .finance-term').first
        dark_trigger.click()
        check('term_dialog_dark', page.locator('#term-dialog[open]').count() == 1
              and page.locator('#term-definition').inner_text().strip() != '')
        capture('after-term-dark')
        audit('term-dialog-dark')
        page.keyboard.press('Escape')
        check('term_dialog_dark_escape_focus', page.locator('#term-dialog[open]').count() == 0
              and dark_trigger.evaluate('(element) => document.activeElement === element'))
        check('csv_download_embedded', page.locator('a[download][href^="data:text/csv"]').count() > 0)
        page.set_viewport_size({'width': 390, 'height': 844})
        page.evaluate("location.hash='welcome'")
        page.wait_for_timeout(150)
        page.evaluate("""location.hash=document.querySelector(
            '.slide[data-language="ja"] .finance-term').closest('.slide').id""")
        page.wait_for_timeout(150)
        mobile_trigger = page.locator('.slide:visible .finance-term').first
        mobile_trigger.click()
        check('term_dialog_mobile', page.locator('#term-dialog[open]').count() == 1
              and page.locator('#term-definition').inner_text().strip() != ''
              and page.locator('#term-dialog').evaluate(
                  '(dialog) => dialog.getBoundingClientRect().right <= innerWidth'))
        capture('after-term-mobile')
        audit('term-dialog-mobile')
        page.keyboard.press('Escape')
        check('term_dialog_mobile_escape_focus', page.locator('#term-dialog[open]').count() == 0
              and mobile_trigger.evaluate('(element) => document.activeElement === element'))
        page.evaluate("location.hash='welcome'")
        page.wait_for_timeout(150)
        page.locator('#nav-toggle').click()
        capture('after-mobile')
        audit('mobile')
        page.keyboard.press('Escape')
        check('mobile_escape_closes_nav', page.locator('#nav-toggle').get_attribute('aria-expanded') == 'false')
        page.keyboard.press('Tab')
        check('keyboard_focus_visible', page.evaluate("""() => {
            const e=document.activeElement, s=getComputedStyle(e);
            return e.matches(':focus-visible') && s.outlineStyle!=='none' && parseFloat(s.outlineWidth)>=2;
        }"""))
        check('mobile_no_page_overflow', page.evaluate(
            'document.documentElement.scrollWidth <= innerWidth'))
        check('no_console_errors', not report['console_errors'])
        check('zero_network_attempts', not report['network_attempts'])
        broken = browser.new_page()
        broken_errors = []
        broken.on('console', lambda message: broken_errors.append(message.text)
                  if message.type == 'error' else None)
        broken.add_init_script("""document.addEventListener('DOMContentLoaded', () => {
            document.getElementById('image-payloads').textContent='{';
        });""")
        broken.goto(html_path.resolve().as_uri())
        broken.evaluate("""location.hash=[...document.querySelectorAll('.slide')]
                        .find(s=>s.querySelector('.step-image')).id""")
        broken.locator('.image-load-error').first.wait_for()
        check('corrupt_payload_visible_error', broken.locator('.image-load-error:visible').count() > 0
              and len(broken_errors) > 0)
        broken.close()
        browser.close()
    report['passed'] = all(report['checks'].values())
    (output / 'browser-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                                encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--axe', type=Path, required=True, help='local axe-core axe.min.js')
    parser.add_argument('--html', type=Path, default=ROOT / 'docs/workshop-presentation.html')
    args = parser.parse_args()
    report = run(args.output_dir, args.axe, args.html)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
