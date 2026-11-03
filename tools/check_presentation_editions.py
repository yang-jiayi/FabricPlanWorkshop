#!/usr/bin/env python3
"""Verify independently copied participant / instructor offline HTML files."""
import argparse
import json
import shutil
from pathlib import Path

from playwright.sync_api import sync_playwright

from check_presentation_browser import run as browser_checks
from check_presentation_languages import run as language_checks
from check_presentation_typography import run as typography_checks


ROOT = Path(__file__).resolve().parents[1]


def run(output, axe):
    output.mkdir(parents=True, exist_ok=True)
    report = {'editions': {}, 'scope_checks': {}}
    for edition, filename in [('participant', 'workshop-presentation.html'),
                              ('instructor', 'workshop-instructor.html')]:
        folder = output / edition
        folder.mkdir(parents=True, exist_ok=True)
        # Use only this copy, outside the repository and with no sibling edition.
        standalone = folder / filename
        shutil.copyfile(ROOT / 'docs' / filename, standalone)
        report['editions'][edition] = {
            'bytes': standalone.stat().st_size,
            'browser': browser_checks(folder / 'browser', axe, standalone),
            'languages': language_checks(folder / 'languages', axe, standalone),
            'typography': typography_checks(folder / 'typography', html_path=standalone),
        }
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(channel='msedge')
            page = browser.new_page(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
            page.goto(standalone.as_uri())
            page.wait_for_function("document.documentElement.classList.contains('js')")
            for locale in ('ja', 'en'):
                page.locator('#language-select').select_option(locale)
                label = (('参加者用' if edition == 'participant' else '講師用') if locale == 'ja'
                         else ('Participant edition' if edition == 'participant' else 'Instructor edition'))
                prefix = f'{edition}_{locale}_'
                report['scope_checks'][prefix + 'visible_edition_label'] = page.locator(
                    '.edition-label').inner_text() == label
                report['scope_checks'][prefix + 'instructor_scope'] = (
                    page.locator(f'.slide[data-language="{locale}"][data-lab="facilitator"]').count()
                    == (14 if edition == 'instructor' else 0))
                page.screenshot(path=str(folder / f'{locale}-home.png'))
                page.keyboard.press('Control+k')
                page.locator('#global-search-input').fill('9,317')
                page.wait_for_timeout(150)
                report['scope_checks'][prefix + 'cost_search_scope'] = (
                    page.locator('#search-results [role="option"]').count() > 0) == (edition == 'instructor')
                page.keyboard.press('Escape')
                # Locate the knowledge check by content rather than assuming a new article ID.
                page.evaluate("""locale => location.hash=[...document.querySelectorAll(
                    `.slide[data-language="${locale}"][data-lab="lab00"]`)].find(
                    s=>s.dataset.title.includes(locale==='ja'?'理解度':'Knowledge')).id""", locale)
                page.wait_for_timeout(100)
                report['scope_checks'][prefix + 'questions_retained'] = (
                    page.locator('.slide:visible .prose ol > li').count() >= 6)
                report['scope_checks'][prefix + 'answer_boundary'] = (
                    page.locator('.slide:visible summary').filter(
                        has_text='解答' if locale == 'ja' else 'Answers').count()
                    == (1 if edition == 'instructor' else 0))
                if edition == 'instructor':
                    page.locator('.slide:visible summary').filter(
                        has_text='解答' if locale == 'ja' else 'Answers').click()
                page.screenshot(path=str(folder / f'{locale}-knowledge-check.png'))
                if edition == 'instructor':
                    page.evaluate("locale=>location.hash=(locale==='en'?'en-':'')+'facilitator-s007'", locale)
                    page.wait_for_timeout(100)
                    page.screenshot(path=str(folder / f'{locale}-agenda.png'))
                    page.evaluate("locale=>location.hash=(locale==='en'?'en-':'')+'facilitator-s011'", locale)
                    page.wait_for_timeout(100)
                    page.screenshot(path=str(folder / f'{locale}-costs.png'))
                page.set_viewport_size({'width': 390, 'height': 844})
                page.evaluate("locale=>location.hash=(locale==='en'?'en-':'')+'welcome'", locale)
                page.wait_for_timeout(100)
                report['scope_checks'][prefix + 'mobile_edition_visible'] = (
                    page.locator('.edition-label').is_visible() and
                    page.locator('.edition-label').inner_text() == label)
                report['scope_checks'][prefix + 'mobile_no_overflow'] = page.evaluate(
                    'document.documentElement.scrollWidth<=innerWidth')
                page.screenshot(path=str(folder / f'{locale}-mobile.png'))
                page.set_viewport_size({'width': 1440, 'height': 1000})
            browser.close()
    report['passed'] = all(report['scope_checks'].values()) and all(
        suite['passed'] for edition in report['editions'].values()
        for suite in [edition['browser'], edition['languages'], edition['typography']])
    (output / 'edition-report.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--axe', type=Path, required=True)
    args = parser.parse_args()
    report = run(args.output_dir, args.axe)
    print(json.dumps({'passed': report['passed'], 'scope_checks': report['scope_checks']},
                     ensure_ascii=False, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
