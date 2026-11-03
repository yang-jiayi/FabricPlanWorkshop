#!/usr/bin/env python3
"""Exercise complete offline Japanese / English switching in local Edge."""
import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]


def run(output, axe):
    output.mkdir(parents=True, exist_ok=True)
    report = {'checks': {}, 'errors': [], 'network': [], 'accessibility': {}}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel='msedge')
        page = browser.new_page(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
        page.on('pageerror', lambda error: report['errors'].append(str(error)))
        page.on('console', lambda message: report['errors'].append(message.text)
                if message.type == 'error' else None)
        page.on('request', lambda request: report['network'].append(request.url)
                if request.url.startswith(('http:', 'https:')) else None)
        page.goto((ROOT / 'docs/workshop-presentation.html').as_uri())
        page.wait_for_function("document.documentElement.classList.contains('js')")

        def check(name, passed):
            report['checks'][name] = bool(passed)
            (output / 'language-report.json').write_text(
                json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

        def capture(name):
            page.screenshot(path=str(output / (name + '.png')), animations='disabled')

        def audit(name):
            page.add_script_tag(path=str(axe))
            violations = page.evaluate("""async () => (await axe.run(document, {
                runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}
            })).violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>n.target)}))""")
            report['accessibility'][name] = violations
            check(name + '_axe', not violations)

        check('default_japanese', page.locator('html').get_attribute('lang') == 'ja')
        check('single_registry', page.locator('#image-payloads').count() == 1)
        check('full_article_parity', page.evaluate("""() => {
            const ids=lang=>[...document.querySelectorAll(`.slide[data-language="${lang}"]`)]
                .map(s=>s.dataset.article).sort();
            return JSON.stringify(ids('ja'))===JSON.stringify(ids('en'));
        }"""))
        check('complete_english_prose', page.evaluate("""() => {
            const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
            while(walker.nextNode()) {
                const node=walker.currentNode, parent=node.parentElement;
                if(parent.closest('.slide[data-language="en"]') && !parent.closest('code,pre') &&
                    /[\\u3040-\\u30ff\\u3400-\\u9fff]/.test(node.textContent)) return false;
            }
            return true;
        }"""))
        for width, name in [(1440, 'desktop'), (390, 'mobile')]:
            page.set_viewport_size({'width': width, 'height': 1000 if width == 1440 else 844})
            page.locator('#language-select').select_option('ja')
            page.evaluate("location.hash='lab09-s002'")
            page.wait_for_timeout(100)
            japanese_title = page.locator('.slide:visible h1').inner_text()
            capture(name + '-ja-lab09')
            page.keyboard.press('Control+k')
            page.locator('#global-search-input').fill('Forecast Gross')
            page.wait_for_timeout(150)
            page.keyboard.press('Enter')
            check(name + '_japanese_search', page.locator('#search-dialog[open]').count() == 0)
            page.evaluate("location.hash='lab09-s002'")
            page.wait_for_timeout(100)
            page.locator('#language-select').select_option('en')
            check(name + '_english_article_correspondence',
                  page.evaluate('location.hash') == '#en-lab09-s002')
            check(name + '_document_lang', page.locator('html').get_attribute('lang') == 'en')
            check(name + '_one_visible_article', page.locator('.slide:visible').count() == 1)
            check(name + '_english_title', not page.locator('.slide:visible h1').evaluate(
                "(e)=>/[\\u3040-\\u30ff\\u3400-\\u9fff]/.test(e.textContent)"))
            check(name + '_translated_navigation', page.locator('.chapter-list').evaluate(
                "(e)=>e.textContent.includes('Module') && !/[\\u3040-\\u30ff\\u3400-\\u9fff]/.test(e.textContent)"))
            check(name + '_search_state_cleared', page.locator('#global-search-input').input_value() == ''
                  and page.locator('mark.article-hit').count() == 0)
            check(name + '_no_page_overflow', not page.evaluate('document.documentElement.scrollWidth>innerWidth'))
            check(name + '_english_578_images',
                  page.locator('.slide[data-language="en"] img[data-image]').count() == 578)
            if width == 390:
                page.locator('#nav-toggle').click()
                page.locator('#nav-filter').fill('Governance')
                check('mobile_english_nav_filter', page.locator('.chapter-group:visible').count() == 1)
                capture('mobile-en-navigation')
                audit('mobile-en-navigation')
                check('mobile_english_sidebar_reflow', page.locator('#sidebar').evaluate(
                    '(e)=>e.scrollWidth<=e.clientWidth'))
                page.locator('#nav-filter').fill('')
                page.keyboard.press('Escape')
            capture(name + '-en-lab09')
            audit(name + '-en-lab')
            page.keyboard.press('Control+k')
            page.locator('#global-search-input').fill('synthetic CSV')
            page.wait_for_timeout(150)
            check(name + '_english_body_search', page.locator('#search-results [role="option"]').count() > 0)
            check(name + '_english_search_labels', 'articles' in page.locator('#search-status').inner_text())
            capture(name + '-en-search')
            audit(name + '-en-search')
            page.keyboard.press('ArrowDown')
            page.keyboard.press('Enter')
            check(name + '_english_keyboard_jump', page.locator('.slide:visible mark').count() > 0)
            page.evaluate("location.hash='en-index'")
            page.wait_for_timeout(100)
            check(name + '_english_index', 'Allocation' in page.locator('#en-index').inner_text()
                  and 'Semantic model' in page.locator('#en-index').inner_text())
            page.locator('#en-index .index-entry summary').first.click()
            page.locator('#en-index .index-entry[open] a').first.click()
            check(name + '_english_index_link', page.evaluate('location.hash').startswith('#en-'))
            page.evaluate("location.hash='en-index'")
            page.wait_for_timeout(100)
            capture(name + '-en-index')
            audit(name + '-en-index')
            page.evaluate("""location.hash=[...document.querySelectorAll('.slide[data-language="en"]')]
                          .find(s=>s.querySelector('.copy-code')).id""")
            page.wait_for_timeout(100)
            page.locator('.slide:visible .copy-code').first.click()
            page.wait_for_function("""() => /Copied|Could not copy/.test(
                document.querySelector('.slide:not([hidden]) .copy-code').textContent)""")
            check(name + '_english_copy', page.locator('.slide:visible .copy-code').first.inner_text() == 'Copied')
            page.evaluate("""location.hash=[...document.querySelectorAll('.slide[data-language="en"]')]
                          .find(s=>s.querySelector('a[download*="sample.csv"]')).id""")
            page.wait_for_timeout(100)
            with page.expect_download() as downloaded:
                page.locator('.slide:visible a[download*="sample.csv"]').first.click()
            check(name + '_english_csv', Path(downloaded.value.path()).read_bytes() ==
                  (ROOT / 'data/lab09-variance-snapshot-sample.csv').read_text(encoding='utf-8').encode('utf-8'))
            page.evaluate("""location.hash=[...document.querySelectorAll('.slide[data-language="en"]')]
                          .find(s=>s.querySelector('.shot')).id""")
            page.wait_for_timeout(100)
            page.locator('.slide:visible .shot').first.click()
            page.locator('#zoom-image').wait_for()
            check(name + '_english_image_caption', not page.locator('#image-caption').evaluate(
                "(e)=>/[\\u3040-\\u30ff\\u3400-\\u9fff]/.test(e.textContent)"))
            capture(name + '-en-lightbox')
            audit(name + '-en-lightbox')
            page.keyboard.press('Escape')
            page.evaluate("location.hash='en-welcome'")
            page.wait_for_timeout(100)
            capture(name + '-en-home')
            if page.locator('#theme-toggle').get_attribute('data-mode') != 'dark':
                page.locator('#theme-toggle').click()
                if page.locator('#theme-toggle').get_attribute('data-mode') != 'dark':
                    page.locator('#theme-toggle').click()
            capture(name + '-en-dark')
            audit(name + '-en-dark')
            page.evaluate("location.hash='en-lab09-s002'")
            page.wait_for_timeout(100)
            page.locator('#language-select').select_option('ja')
            check(name + '_return_correspondence', page.evaluate('location.hash') == '#lab09-s002'
                  and page.locator('.slide:visible h1').inner_text() == japanese_title)
            check(name + '_japanese_navigation_restored', 'モジュール' in page.locator('.chapter-list').text_content())
            page.evaluate("location.hash='lab01-s001'")
            page.wait_for_timeout(100)
            page.locator('#language-select').select_option('en')
            page.evaluate("location.hash='en-lab09-s002'")
            page.wait_for_timeout(100)
            history_length = page.evaluate('history.length')
            for expected in ['#en-lab01-s001', '#lab01-s001']:
                page.evaluate('history.back()')
                page.wait_for_function('(hash)=>location.hash===hash', arg=expected)
                page.wait_for_timeout(50)
                check(name + '_back_' + expected[1:], page.locator('.slide:visible').get_attribute('id') == expected[1:])
            for expected in ['#en-lab01-s001', '#en-lab09-s002']:
                page.evaluate('history.forward()')
                page.wait_for_function('(hash)=>location.hash===hash', arg=expected)
                page.wait_for_timeout(50)
                check(name + '_forward_' + expected[1:], page.locator('.slide:visible').get_attribute('id') == expected[1:])
            check(name + '_history_not_rewritten', page.evaluate('history.length') == history_length)
            for locale in ['ja', 'en']:
                page.locator('#language-select').select_option(locale)
                page.emulate_media(media='print')
                check(name + '_print_' + locale, page.locator(
                    f'.slide[data-language="{locale}"]:visible').count() > 200 and
                    page.locator(f'.slide[data-language="{"en" if locale == "ja" else "ja"}"]:visible').count() == 0)
                page.emulate_media(media='screen')
            page.locator('#language-select').select_option('en')
            page.reload()
            page.wait_for_function("document.documentElement.classList.contains('js')")
            check(name + '_selection_persists', page.locator('html').get_attribute('lang') == 'en'
                  and page.locator('.slide:visible').get_attribute('data-article') == 'lab09-s002')
        check('no_console_errors', not report['errors'])
        check('no_network', not report['network'])
        browser.close()
    report['passed'] = all(report['checks'].values())
    (output / 'language-report.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--axe', type=Path, required=True)
    args = parser.parse_args()
    report = run(args.output_dir, args.axe)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
