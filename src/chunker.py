import re
from typing import List, Tuple

CODE_BLOCK_RE = re.compile(r"```[a-zA-Z]*\n[\s\S]*?\n```")
SENTENCE_END_RE = re.compile(r"\.[ \n]")


def _find_code_blocks(text: str) -> List[tuple[int, int]]:
    """Find all code block positions in the text.

    Args:
        text (str): The text to search for code blocks.

    Returns:
        List[tuple[int, int]]: List of (start, end) positions of code blocks.
    """
    return [(m.start(), m.end()) for m in CODE_BLOCK_RE.finditer(text)]


def _split_paragraphs(text: str) -> List[str]:
    """Return non-empty paragraphs separated by two successive newlines.

    Args:
        text (str): The input text to split into paragraphs.

    Returns:
        List[str]: A list of non-empty paragraphs.
    """
    return [p for p in text.split("\n\n") if p]


def _split_long_text(text: str, chunk_size: int) -> Tuple[List[str], str]:
    """Split text into chunks no larger than chunk_size, preferring sentence boundaries.

    The function avoids splitting inside code blocks. If a code block is encountered,
    it will be kept intact even if it exceeds the chunk_size.

    Args:
        text (str): The text to split.
        chunk_size (int): Maximum allowed size (in characters) of each chunk.

    Returns:
        Tuple[List[str], str]:
            - List[str]: All full-size chunks.
            - str: The last piece (always < chunk_size) as remainder.
    """
    chunks: List[str] = []
    remainder = text
    code_blocks = _find_code_blocks(text)

    while len(remainder) > chunk_size:
        window = remainder[:chunk_size]

        # Check if we're in the middle of a code block
        for start, end in code_blocks:
            relative_start = start - (len(text) - len(remainder))
            relative_end = end - (len(text) - len(remainder))

            # If the window cuts through a code block, extend it to include the whole block
            if 0 <= relative_start < chunk_size < relative_end:
                window = remainder[:relative_end]
                match = None
                break
        else:
            # If not in a code block, try to find the last sentence boundary
            match = SENTENCE_END_RE.search(window)

        cut_index = match.end() if match else len(window)
        chunks.append(remainder[:cut_index].strip())
        remainder = remainder[cut_index:]

    return chunks, remainder


def chunk_text(text: str, chunk_size: int = 5000) -> List[str]:
    """Split text into chunks whose length is at most chunk_size.

    The algorithm tries, in that order:
      1. Keep paragraphs together (paragraph = two successive newlines).
      2. Keep code blocks intact (text between ```).
      3. If a single paragraph is still too large, split on sentence boundaries.

    Args:
        text (str): The input text to split.
        chunk_size (int, optional): Maximum allowed size (in characters) of each chunk. Defaults to 5000.

    Returns:
        List[str]: A list of text chunks maintaining the original order.
    """
    if not text:
        return []

    paragraphs = _split_paragraphs(text)

    chunks: List[str] = []
    buffer = ""

    for paragraph in paragraphs:
        candidate = f"{buffer}\n\n{paragraph}" if buffer else paragraph

        if len(candidate) <= chunk_size:
            buffer = candidate
            continue

        if buffer:
            chunks.append(buffer.strip())

        big_chunks, remainder = _split_long_text(paragraph, chunk_size)
        chunks.extend(big_chunks)

        buffer = remainder

    if buffer:
        chunks.append(buffer.strip())

    return chunks
