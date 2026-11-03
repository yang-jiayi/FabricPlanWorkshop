#!/usr/bin/env python3
"""Verify fluid Japanese typography and responsive reflow in local Edge."""
import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
VIEWPORTS = {'mobile': (390, 844), 'tablet': (768, 1024), 'compact': (1280, 1000),
             'desktop': (1440, 1000), 'large': (1920, 1080)}


def run(output, capture_only=False, html_path=ROOT / 'docs/workshop-presentation.html'):
    output.mkdir(parents=True, exist_ok=True)
    report = {'viewports': {}, 'checks': {}, 'errors': []}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel='msedge')
        page = browser.new_page(reduced_motion='reduce')
        page.on('pageerror', lambda error: report['errors'].append(str(error)))
        page.goto(html_path.resolve().as_uri())
        page.wait_for_function("document.documentElement.classList.contains('js')")

        def capture(name):
            page.screenshot(path=str(output / (name + '.png')), animations='disabled')

        def metrics():
            return page.evaluate("""() => {
                const measure=selector => {
                    const e=document.querySelector(selector), s=getComputedStyle(e);
                    return {family:s.fontFamily, size:parseFloat(s.fontSize),
                        lineHeight:parseFloat(s.lineHeight)||null, width:e.getBoundingClientRect().width};
                };
                return {prose:measure('.welcome .prose'), heading:measure('#welcome-title'),
                    navigation:measure('.section-link'), control:measure('#theme-toggle'),
                    caption:measure('.shot-caption'), search:measure('#global-search-input'),
                    code:measure('pre code'), root:measure('html'),
                    overflow:document.documentElement.scrollWidth>innerWidth};
            }""")

        cdp = page.context.new_cdp_session(page)
        cdp.send('DOM.enable')
        cdp.send('CSS.enable')
        document = cdp.send('DOM.getDocument')
        prose_node = cdp.send('DOM.querySelector', {
            'nodeId': document['root']['nodeId'], 'selector': '.welcome .prose p',
        })
        report['rendered_fonts'] = cdp.send('CSS.getPlatformFontsForNode', {
            'nodeId': prose_node['nodeId'],
        })['fonts']

        for name, (width, height) in VIEWPORTS.items():
            page.set_viewport_size({'width': width, 'height': height})
            page.evaluate("location.hash='welcome'")
            page.wait_for_timeout(100)
            report['viewports'][name] = metrics()
            capture(name + '-home')
            page.evaluate("""location.hash=[...document.querySelectorAll('.slide[data-lab="lab09"]')]
                          .find(s=>s.querySelector('.prose table')).id""")
            page.wait_for_timeout(100)
            capture(name + '-lab')
            report['checks'][name + '_lab_reflow'] = not page.evaluate(
                'document.documentElement.scrollWidth>innerWidth')
            page.keyboard.press('Control+k')
            page.locator('#global-search-input').fill('Forecast Gross')
            page.wait_for_timeout(150)
            capture(name + '-search')
            report['checks'][name + '_search_reflow'] = page.locator('#search-dialog').evaluate(
                '(d) => d.scrollWidth<=d.clientWidth')
            page.keyboard.press('ArrowDown')
            page.keyboard.press('Enter')
            report['checks'][name + '_keyboard_search'] = page.locator('#search-dialog[open]').count() == 0
            page.evaluate("location.hash='index'")
            page.wait_for_timeout(100)
            page.locator('.index-entry:visible summary').last.click()
            capture(name + '-index')
            report['checks'][name + '_index_reflow'] = not page.evaluate(
                'document.documentElement.scrollWidth>innerWidth')
            if width <= 850:
                page.locator('#nav-toggle').click()
                page.locator('#nav-filter').fill('Lab09')
                capture(name + '-navigation')
                report['checks'][name + '_navigation_reflow'] = page.locator('#sidebar').evaluate(
                    '(e) => e.scrollWidth<=e.clientWidth')
                page.locator('#nav-filter').fill('')
                page.keyboard.press('Escape')
            page.locator('#theme-toggle').click()
            if page.locator('html').get_attribute('data-theme') != 'dark':
                page.locator('#theme-toggle').click()
            capture(name + '-dark')
            while page.locator('#theme-toggle').get_attribute('data-mode') != 'light':
                page.locator('#theme-toggle').click()
        if not capture_only:
            for name, value in report['viewports'].items():
                for role in ('prose', 'heading', 'navigation', 'control', 'caption', 'search'):
                    report['checks'][name + '_' + role + '_font'] = value[role]['family'].startswith('"Yu Gothic UI"')
                report['checks'][name + '_readable_body'] = 17 <= value['prose']['size'] <= 20
                report['checks'][name + '_readable_ui'] = min(value[role]['size'] for role in
                    ('navigation', 'control', 'caption', 'search')) >= 14
                report['checks'][name + '_comfortable_leading'] = value['prose']['lineHeight'] / value['prose']['size'] >= 1.8
                report['checks'][name + '_monospace'] = 'Consolas' in value['code']['family']
            report['checks']['fluid_growth'] = (
                report['viewports']['mobile']['prose']['size'] <
                report['viewports']['desktop']['prose']['size'] <=
                report['viewports']['large']['prose']['size'] <= 20)
            report['checks']['bounded_desktop_line_length'] = report['viewports']['large']['prose']['width'] <= 900
            # A 720 CSS-pixel viewport is the reflow space of a 1440px window at 200% zoom.
            page.set_viewport_size({'width': 720, 'height': 500})
            page.evaluate("location.hash='welcome'")
            page.wait_for_timeout(100)
            capture('zoom-200-reflow')
            report['checks']['zoom_200_reflow'] = not page.evaluate(
                'document.documentElement.scrollWidth>innerWidth')
            page.evaluate("document.documentElement.style.fontSize='200%'")
            page.wait_for_timeout(100)
            capture('font-preference-200')
            preferred = metrics()
            report['font_preference_200'] = preferred
            report['checks']['font_preference_respected'] = preferred['prose']['size'] >= 34
            report['checks']['font_preference_reflow'] = not preferred['overflow']
        browser.close()
    report['passed'] = not report['errors'] and all(report['checks'].values())
    (output / 'typography-report.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--capture-only', action='store_true', help='record baseline without type assertions')
    parser.add_argument('--html', type=Path, default=ROOT / 'docs/workshop-presentation.html')
    args = parser.parse_args()
    report = run(args.output_dir, args.capture_only, args.html)
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if args.capture_only or report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
