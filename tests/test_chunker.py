import pytest

from chunker import chunk_text


def test_chunk_text_basic_split():
    text = "A" * 1000 + "\n\n" + "B" * 1000 + "\n\n" + "C" * 1000
    chunks = chunk_text(text, chunk_size=1000)
    # Should split at paragraph breaks
    assert len(chunks) == 3
    assert chunks[0] == "A" * 1000
    assert chunks[1] == "B" * 1000
    assert chunks[2] == "C" * 1000

def test_chunk_text_code_block_boundary():
    text = "Some intro.\n\n```python\nprint('Hello')\n```\n\nSome more text."
    # Force a small chunk size to test code block boundary
    chunks = chunk_text(text, chunk_size=30)
    # Should split at code block boundary
    assert any("```python" in chunk for chunk in chunks)
    assert any("print('Hello')" in chunk for chunk in chunks)

def test_chunk_text_sentence_boundary():
    text = "This is a sentence. This is another. And another."
    chunks = chunk_text(text, chunk_size=25)
    # Should split at sentence boundary
    assert all(len(chunk) <= 25 for chunk in chunks)
    assert chunks[0].endswith(".")
    assert len(chunks) > 1

def test_chunk_text_no_split_needed():
    text = "Short text."
    chunks = chunk_text(text, chunk_size=100)
    assert chunks == ["Short text."]

def test_chunk_text_empty_string():
    assert chunk_text("") == []

def test_chunk_text_exact_chunk_size():
    text = "A" * 50
    chunks = chunk_text(text, chunk_size=50)
    assert chunks == ["A" * 50]

def test_chunk_text_long_text_with_no_breaks():
    text = "A" * 120
    chunks = chunk_text(text, chunk_size=50)
    # Should split at max size if no breaks
    assert all(len(chunk) <= 50 for chunk in chunks)
    assert "".join(chunks) == text
