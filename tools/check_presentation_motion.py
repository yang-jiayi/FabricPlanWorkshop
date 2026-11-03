#!/usr/bin/env python3
"""Check finite shuffle/highlight motion and unmodified icons in local Edge."""
import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]


def run(output, html_path):
    output.mkdir(parents=True, exist_ok=True)
    report = {'checks': {}, 'errors': []}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel='msedge')
        page = browser.new_page(viewport={'width': 1440, 'height': 1000}, reduced_motion='no-preference')
        page.on('pageerror', lambda error: report['errors'].append(str(error)))
        page.goto(html_path.resolve().as_uri())
        page.wait_for_function("document.documentElement.classList.contains('js')")

        def check(name, passed):
            report['checks'][name] = bool(passed)

        def icons_unchanged():
            return page.evaluate("""() => [...document.querySelectorAll(
                'img[src^="data:image/svg+xml"]')].every(image => {
                for(let node=image;node;node=node.parentElement) {
                    const s=getComputedStyle(node);
                    if(s.filter!=='none' || s.rotate!=='none') return false;
                    if(s.scale!=='none') {
                        const values=s.scale.split(' ').map(Number);
                        if(values.some(n=>n<=0) || (values.length>1 && values[0]!==values[1])) return false;
                    }
                    if(s.transform!=='none') {
                        const m=new DOMMatrixReadOnly(s.transform);
                        if(!m.is2D || Math.abs(m.b)>0.001 || Math.abs(m.c)>0.001 ||
                           m.a<=0 || Math.abs(m.a-m.d)>0.001) return false;
                    }
                }
                return true;
            })""")

        for locale in ('ja', 'en'):
            page.locator('#language-select').select_option(locale)
            page.evaluate("locale=>location.hash=(locale==='en'?'en-':'')+'welcome'", locale)
            page.wait_for_timeout(80)
            animations = page.evaluate("""() => document.getAnimations().map(a=>({
                name:a.animationName,iterations:a.effect.getTiming().iterations,
                duration:a.effect.getTiming().duration}))""")
            check(locale + '_gradient_motion', any(a['name'] == 'gradient-arrival' for a in animations))
            check(locale + '_shuffle_motion', any(a['name'] == 'card-shuffle' for a in animations))
            check(locale + '_finite_durations', all(a['iterations'] == 1 and a['duration'] <= 5000
                                                    for a in animations))
            page.evaluate("document.getAnimations().forEach(a=>{a.pause();a.currentTime=240;})")
            check(locale + '_mid_shuffle_icons_unmodified', icons_unchanged())
            page.screenshot(path=str(output / f'{locale}-shuffle-frame.png'))
            page.emulate_media(media='print')
            check(locale + '_mid_shuffle_print_is_static', page.locator(
                f'.slide[data-language="{locale}"] .product-grid > div').first.evaluate(
                "(e)=>{const s=getComputedStyle(e);return s.opacity==='1' && s.transform==='none' && s.animationName==='none'}"))
            page.emulate_media(media='screen')
            page.evaluate("document.getAnimations().forEach(a=>a.finish())")
            check(locale + '_all_motion_finishes', page.evaluate(
                "document.getAnimations().every(a=>a.playState==='finished')"))
            check(locale + '_settled_icons_unmodified', icons_unchanged())
            page.screenshot(path=str(output / f'{locale}-settled-home.png'))
            page.evaluate("locale=>location.hash=(locale==='en'?'en-':'')+'workshop-index'", locale)
            page.wait_for_timeout(80)
            check(locale + '_lab_card_shuffle', page.locator('.slide:visible .toc-card').first.evaluate(
                "(e)=>getComputedStyle(e).animationName==='card-shuffle'"))
            page.evaluate("document.getAnimations().forEach(a=>{a.pause();a.currentTime=200;})")
            check(locale + '_mid_lab_icons_unmodified', icons_unchanged())
            page.screenshot(path=str(output / f'{locale}-lab-cards-frame.png'))
            page.evaluate("document.getAnimations().forEach(a=>a.finish())")
            page.keyboard.press('Control+k')
            page.locator('#global-search-input').fill('Forecast Gross')
            page.wait_for_timeout(150)
            check(locale + '_search_highlight_pulse', page.locator('#search-results mark').first.evaluate(
                "(e)=>getComputedStyle(e).animationName==='hit-pulse'"))
            page.keyboard.press('Enter')
            page.wait_for_timeout(80)
            check(locale + '_article_hit_pulse', page.locator('.slide:visible mark.article-hit').first.evaluate(
                "(e)=>getComputedStyle(e).animationName==='hit-pulse'"))
            page.emulate_media(reduced_motion='reduce')
            page.evaluate("locale=>location.hash=(locale==='en'?'en-':'')+'welcome'", locale)
            page.wait_for_timeout(80)
            check(locale + '_reduced_motion_stops_animations', page.evaluate(
                "document.getAnimations().every(a=>a.playState!=='running')"))
            check(locale + '_reduced_motion_static_cards', page.locator('.slide:visible .product-grid > div').first.evaluate(
                "(e)=>{const s=getComputedStyle(e);return s.animationName==='none' && s.transform==='none' && s.opacity==='1'}"))
            check(locale + '_reduced_motion_same_information', page.locator('.slide:visible .product-grid img').count() == 9)
            check(locale + '_reduced_icons_unmodified', icons_unchanged())
            page.screenshot(path=str(output / f'{locale}-reduced-home.png'))
            page.set_viewport_size({'width': 390, 'height': 844})
            check(locale + '_mobile_reflow', page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
            page.screenshot(path=str(output / f'{locale}-mobile.png'))
            page.set_viewport_size({'width': 1440, 'height': 1000})
            page.emulate_media(reduced_motion='no-preference')
        browser.close()
    report['passed'] = not report['errors'] and all(report['checks'].values())
    (output / 'motion-report.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--html', type=Path, default=ROOT / 'docs/workshop-presentation.html')
    args = parser.parse_args()
    report = run(args.output_dir, args.html)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
