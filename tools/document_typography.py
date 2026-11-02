"""Compare archived source quotes using the two approved typography changes."""


def normalize_source_quote(text):
    return text.replace('\u30fb', ',').replace('\uff0f', ' / ')


def same_source_quote(actual, saved):
    return normalize_source_quote(actual) == normalize_source_quote(saved)
