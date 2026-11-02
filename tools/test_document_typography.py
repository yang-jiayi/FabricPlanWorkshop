import unittest

from document_typography import normalize_source_quote, same_source_quote


class SourceQuoteTypographyTests(unittest.TestCase):
    def test_only_the_two_requested_symbols_are_equivalent(self):
        saved = 'Source\uff0fCopy\u30fb25.90m'
        self.assertTrue(same_source_quote('Source / Copy,25.90m', saved))
        self.assertTrue(same_source_quote(saved, 'Source / Copy,25.90m'))
        self.assertEqual(normalize_source_quote(saved), 'Source / Copy,25.90m')

    def test_changed_numbers_and_meaning_are_rejected(self):
        saved = 'Source\uff0fCopy\u30fb25.90m'
        for actual in ['Source / Copy,25.91m', 'Source / Model,25.90m', 'source / Copy,25.90m']:
            with self.subTest(actual=actual):
                self.assertFalse(same_source_quote(actual, saved))

    def test_other_whitespace_and_symbols_are_rejected(self):
        saved = 'Source\uff0fCopy\u30fb25.90m'
        for actual in [' Source / Copy,25.90m', 'Source/Copy,25.90m',
                       'Source  / Copy,25.90m', 'Source / Copy\uff0c25.90m',
                       'Source / Copy,25.90m\n']:
            with self.subTest(actual=actual):
                self.assertFalse(same_source_quote(actual, saved))

    def test_unchanged_non_target_unicode_remains_exact(self):
        text = '金額\u00a0A\u2014B / C,1.00'
        self.assertEqual(normalize_source_quote(text), text)
        self.assertFalse(same_source_quote(text, text.replace('\u00a0', ' ')))


if __name__ == '__main__':
    unittest.main()
