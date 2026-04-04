import os
import pytest

from chunking import split_sections, clean_text, read_bdf_text
from query_expansion import expand_query


def test_split_sections_basic():
    text = "CHAPTER 1.\nINTRODUCTION\n1.1\nHello world.\n1.2\nGoodbye world."
    sections = split_sections(text)
    assert any(s['section'].startswith('1.1') for s in sections)
    assert any(s['section'].startswith('1.2') for s in sections)


def test_clean_text_strip_page_numbers():
    raw = "1\nThis is text.\n2\nMore text."
    cleaned, page_map = clean_text(raw)
    assert "1" not in cleaned.split('\n')[0]
    assert 'This is text.' in cleaned


def test_read_bdf_text_exists(tmp_path):
    fpath = tmp_path / 'example.bdf'
    fpath.write_text('sample bdf text', encoding='utf-8')
    result = read_bdf_text(str(fpath))
    assert result == 'sample bdf text'


def test_expand_query_sgd():
    r = expand_query('Explain SGD')
    assert 'stochastic gradient descent' in r['expanded']
    assert 'optimization algorithm' in r['rewrite'] or 'stochastic gradient descent' in r['rewrite']
