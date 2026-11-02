# Copilot contributor guide

This repository contains a Japanese-language Microsoft Fabric Planning workshop for Japanese customers considering an introduction.

- Keep changes focused on the workshop's learner-facing content and preserve the meaning of procedures, expected values, UI labels, and product statements.
- Write clear Japanese. Use ASCII `,` and ` / ` as separators, and follow [LOCALIZATION.md](../LOCALIZATION.md) for product terminology and attribution.
- Keep original-source attribution distinct from additions or corrections in the Japanese edition. Do not present environment-dependent behavior as universal.
- Keep screenshots relevant to a learner's procedure, use descriptive alternative text, and remove customer names, account details, tenant identifiers, and other private information.
- Before submitting documentation changes, run:
  - `python tools/validate_docs.py`
  - `python -m unittest discover -s tools -p "test_*.py"`
  - `python tools/check_public_hygiene.py`
