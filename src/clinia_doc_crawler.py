import asyncio
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List
from urllib.parse import urlparse
from xml.etree import ElementTree

import html2text
import requests
from dotenv import load_dotenv

from chunker import chunk_text
from utils import get_clients, get_env_var

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("clinia-doc-crawler")

openai_client, supabase = get_clients()

embedding_model = get_env_var("EMBEDDING_MODEL") or "text-embedding-3-small"

html_converter = html2text.HTML2Text()
html_converter.ignore_links = False
html_converter.ignore_images = False
html_converter.ignore_tables = False
html_converter.body_width = 0  # No wrapping


@dataclass
class ProcessedChunk:
    url: str
    chunk_number: int
    title: str
    summary: str
    content: str
    metadata: Dict[str, Any]
    embedding: List[float]


async def get_title_and_summary(chunk: str, url: str) -> Dict[str, str]:
    """
    Asynchronously extract the title and summary from a documentation chunk using GPT-4.

    Args:
        chunk (str): The text of the chunk to analyze.
        url (str): The source URL of the chunk.

    Returns:
        Dict[str, str]: A dictionary containing the keys 'title' and 'summary'.
    """
    system_prompt = """You are an AI that extracts titles and summaries from documentation chunks.\n    Return a JSON object with 'title' and 'summary' keys.\n    For the title: If this seems like the start of a document, extract its title. If it's a middle chunk, derive a descriptive title.\n    For the summary: Create a concise summary of the main points in this chunk.\n    Keep both title and summary concise but informative."""
    try:
        response = await openai_client.chat.completions.create(
            model=get_env_var("PRIMARY_MODEL") or "gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"URL: {url}\n\nContent:\n{chunk[:1000]}...",
                },
            ],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)

    except Exception as e:
        log.error(f"Error getting title and summary: {e}")
        return {"title": "Error processing title", "summary": "Error processing summary"}


async def get_embedding(text: str) -> List[float]:
    """
    Asynchronously retrieve the embedding vector for a given text using OpenAI.

    Args:
        text (str): The text to embed.

    Returns:
        List[float]: The embedding vector for the text.
    """
    try:
        response = await openai_client.embeddings.create(model=embedding_model, input=text)
        return response.data[0].embedding

    except Exception as e:
        log.error(f"Error getting embedding: {e}")
        return [0] * 1536  # Return zero vector on error


async def process_chunk(chunk: str, chunk_number: int, url: str) -> ProcessedChunk:
    """
    Process a text chunk: extract the title, summary, embedding, and build a ProcessedChunk object.

    Args:
        chunk (str): The text of the chunk to process.
        chunk_number (int): The index of the chunk in the document.
        url (str): The source URL of the chunk.

    Returns:
        ProcessedChunk: The object containing all extracted and computed information for this chunk.
    """
    extracted = await get_title_and_summary(chunk, url)
    embedding = await get_embedding(chunk)

    metadata = {
        "source": "clinia_docs",
        "chunk_size": len(chunk),
        "crawled_at": datetime.now(timezone.utc).isoformat(),
        "url_path": urlparse(url).path,
    }

    return ProcessedChunk(
        url=url,
        chunk_number=chunk_number,
        title=extracted["title"],
        summary=extracted["summary"],
        content=chunk,
        metadata=metadata,
        embedding=embedding,
    )


async def insert_chunk(chunk: ProcessedChunk):
    """
    Insert a processed chunk into the 'site_pages' table in Supabase.

    Args:
        chunk (ProcessedChunk): The chunk to insert into the database.

    Returns:
        Any: The result of the insert operation or None if an error occurs.
    """
    try:
        data = {
            "url": chunk.url,
            "chunk_number": chunk.chunk_number,
            "title": chunk.title,
            "summary": chunk.summary,
            "content": chunk.content,
            "metadata": chunk.metadata,
            "embedding": chunk.embedding,
        }
        result = supabase.table("site_pages").insert(data).execute()
        log.info(f"Inserted chunk {chunk.chunk_number} for {chunk.url}")
        return result

    except Exception as e:
        log.error(f"Error inserting chunk: {e}")
        return None


async def process_and_store_document(url: str, markdown: str):
    """
    Split a markdown document into chunks, process each chunk, and store them in the database.

    Args:
        url (str): The source URL of the document.
        markdown (str): The markdown content of the document to process.

    Returns:
        None
    """
    chunks = chunk_text(markdown, 1000)

    log.info(f"Split document into {len(chunks)} chunks for {url}")
    tasks = [process_chunk(chunk, i, url) for i, chunk in enumerate(chunks)]

    processed_chunks = await asyncio.gather(*tasks)

    log.info(f"Processed {len(processed_chunks)} chunks for {url}")
    insert_tasks = [insert_chunk(chunk) for chunk in processed_chunks]
    await asyncio.gather(*insert_tasks)
    log.info(f"Stored {len(processed_chunks)} chunks for {url}")


def fetch_url_content(url: str) -> str:
    """
    Retrieve the content of a URL and convert it to markdown.

    Args:
        url (str): The URL to fetch.

    Returns:
        str: The content converted to markdown.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        markdown = html_converter.handle(response.text)
        markdown = re.sub(r"\n{3,}", "\n\n", markdown)
        return markdown

    except requests.RequestException as e:
        raise RuntimeError(f"Error fetching {url}: {str(e)}") from e


async def crawl_parallel_with_requests(urls: List[str], max_concurrent: int = 10):
    """
    Asynchronously crawl multiple URLs in parallel with a concurrency limit.

    Args:
        urls (List[str]): The list of URLs to crawl.
        max_concurrent (int, optional): The maximum number of concurrent tasks. Defaults to 5.

    Returns:
        None
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_url(url: str):
        async with semaphore:
            log.info(f"Crawling: {url}")
            try:
                loop = asyncio.get_running_loop()
                log.info(f"Fetching content from: {url}")
                markdown = await loop.run_in_executor(None, fetch_url_content, url)
                if markdown:
                    log.info(f"Successfully crawled: {url}")
                    await process_and_store_document(url, markdown)
                else:
                    log.warning(f"Failed: {url} - No content retrieved")

            except Exception as e:
                log.error(f"Error processing {url}: {str(e)}")

    log.info(f"Processing {len(urls)} URLs with concurrency {max_concurrent}")
    await asyncio.gather(*[process_url(url) for url in urls])


def get_clinia_docs_urls() -> List[str]:
    """
    Retrieve the list of Clinia documentation URLs from the XML sitemap.

    Returns:
        List[str]: The list of URLs extracted from the sitemap.
    """
    sitemap_url = "https://docs.clinia.com/sitemap.xml"
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        root = ElementTree.fromstring(response.content)
        namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = [loc.text for loc in root.findall(".//ns:loc", namespace)]
        return urls

    except Exception as e:
        log.error(f"Error fetching sitemap: {e}")
        return []


def clear_existing_records():
    """
    Delete existing records from the 'clinia_docs' source in the 'site_pages' table.

    Returns:
        Any: The result of the delete operation or None if an error occurs.
    """
    try:
        result = supabase.table("site_pages").delete().eq("metadata->>source", "clinia_docs").execute()
        log.info("Cleared existing clinia_doc_pages records from site_pages")
        return result

    except Exception as e:
        log.error(f"Error clearing existing records: {e}")
        return None


async def crawl_clinia_docs():
    """
    Main orchestration for crawling: clears old records, fetches URLs, and launches the crawling process.

    Returns:
        None
    """
    try:
        log.info("Starting crawling process...")

        log.info("Clearing existing records…")
        clear_existing_records()

        log.info("Fetching URLs from Clinia docs sitemap…")
        urls = get_clinia_docs_urls()

        if not urls:
            log.warning("No URLs found to crawl")
            return

        log.info(f"Found {len(urls)} URLs to crawl")
        await crawl_parallel_with_requests(urls)
        log.info("Crawling process completed")

    except Exception as e:
        log.error(f"Error in crawling process: {str(e)}")


if __name__ == "__main__":
    asyncio.run(crawl_clinia_docs())
