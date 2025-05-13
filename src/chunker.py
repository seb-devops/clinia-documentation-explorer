
from typing import List


def chunk_text(text: str, chunk_size: int = 5000) -> List[str]:
    """
    Splits a given text into chunks of a specified maximum size, attempting to preserve code blocks and paragraph boundaries.
    Args:
        text (str): The input text to be chunked.
        chunk_size (int, optional): The maximum size of each chunk in characters. Defaults to 5000.
    Returns:
        List[str]: A list of text chunks, each no longer than `chunk_size`, with splits preferably at code block boundaries, paragraph breaks, or sentence ends.
    """
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        if end >= text_length:
            chunks.append(text[start:].strip())
            break
        chunk = text[start:end]
        code_block = chunk.rfind("```")
        if code_block != -1 and code_block > chunk_size * 0.3:
            end = start + code_block
        elif "\n\n" in chunk:
            last_break = chunk.rfind("\n\n")
            if last_break > chunk_size * 0.3:
                end = start + last_break
        elif ". " in chunk:
            last_period = chunk.rfind(". ")
            if last_period > chunk_size * 0.3:
                end = start + last_period + 1
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = max(start + 1, end)
    return chunks
