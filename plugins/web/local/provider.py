"""
Local web content extraction — plugin form (trafilatura / readability / bs4).

Subclasses the plugin-facing :class:`agent.web_search_provider.WebSearchProvider`.

No API key needed. Extracts content directly using:
1. trafilatura (primary) — best-in-class HTML-to-markdown extraction
2. readability-lxml (fallback) — Mozilla's readability algorithm
3. beautifulsoup4 (final fallback) — generic HTML parsing
4. PyMuPDF (fitz) — PDF URL detection and text extraction

All packages are optional dependencies; ``is_available()`` reflects whether
trafilatura is importable (the primary extractor).
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

import httpx

from agent.web_search_provider import WebSearchProvider

logger = logging.getLogger(__name__)

# ─── PDF detection ────────────────────────────────────────────────────────────

PDF_EXTENSIONS = re.compile(r"\.pdf$", re.IGNORECASE)
PDF_CONTENT_TYPES = re.compile(r"application/pdf", re.IGNORECASE)


def _looks_like_pdf(url: str) -> bool:
    """Quick heuristic — URL ends with .pdf or contains a PDF-like path."""
    return bool(PDF_EXTENSIONS.search(url))


# ─── Extractors (lazy-imported so the plugin registers even without deps) ─────


def _extract_with_trafilatura(html: str, url: str) -> Optional[str]:
    """Primary extractor: trafilatura → markdown."""
    try:
        import trafilatura  # type: ignore

        text = trafilatura.extract(
            html,
            url=url,
            output_format="markdown",
            include_links=True,
            include_images=False,
            include_tables=True,
            no_fallback=False,
        )
        if text and text.strip():
            return text.strip()
    except Exception as exc:
        logger.debug("trafilatura extract failed: %s", exc)
    return None


def _extract_with_readability(html: str) -> Optional[str]:
    """Fallback: readability-lxml → plain text."""
    try:
        from readability import Document  # type: ignore

        doc = Document(html)
        content_el = doc.summary()
        if content_el:
            text = content_el.text_content().strip()
            if text:
                return text
    except Exception as exc:
        logger.debug("readability extract failed: %s", exc)
    return None


def _extract_with_bs4(html: str) -> Optional[str]:
    """Final fallback: beautifulsoup4 → text."""
    try:
        from bs4 import BeautifulSoup  # type: ignore

        soup = BeautifulSoup(html, "html.parser")
        # Remove script/style elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        if text:
            # Collapse repeated newlines
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            return "\n".join(lines)
    except Exception as exc:
        logger.debug("BeautifulSoup extract failed: %s", exc)
    return None


def _extract_pdf(content: bytes) -> Optional[str]:
    """Extract text from a PDF buffer using PyMuPDF."""
    try:
        import fitz  # type: ignore

        doc = fitz.open(stream=content, filetype="pdf")
        text_pages: list[str] = []
        for page in doc:
            page_text = page.get_text().strip()
            if page_text:
                text_pages.append(page_text)
        doc.close()
        full = "\n\n".join(text_pages)
        return full if full.strip() else None
    except Exception as exc:
        logger.debug("PyMuPDF extract failed: %s", exc)
    return None


def _extract_content(html: str, url: str) -> str:
    """Run all extractors in priority order, return best result."""
    # trafilatura → readability → bs4
    result = _extract_with_trafilatura(html, url)
    if result:
        return result

    result = _extract_with_readability(html)
    if result:
        return result

    result = _extract_with_bs4(html)
    if result:
        return result

    # Last resort: return cleaned raw text
    try:
        from bs4 import BeautifulSoup  # type: ignore

        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        if text:
            return text[:50000]  # cap at 50k
    except Exception:
        pass

    return ""


# ─── HTTP helpers ─────────────────────────────────────────────────────────────


async def _fetch_url(url: str, timeout: float = 30.0) -> tuple[Optional[str], Optional[bytes], Optional[str]]:
    """Fetch a URL. Returns (html_text, raw_bytes, error_message).
    
    For PDF URLs, returns (None, raw_bytes, None) so the caller can detect PDF.
    """
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (compatible; HermesAgent/1.0; "
                    " +https://hermes-agent.nousresearch.com)"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,application/pdf;q=0.9,"
                    "*/*;q=0.8"
                ),
            },
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()

            content_type = resp.headers.get("content-type", "").lower()

            # PDF detection
            if _looks_like_pdf(url) or PDF_CONTENT_TYPES.search(content_type):
                return None, resp.content, None

            # Try to decode as text
            try:
                text = resp.text
            except Exception:
                text = resp.content.decode("utf-8", errors="replace")

            return text, None, None

    except httpx.TimeoutException:
        return None, None, f"Request timed out after {timeout}s"
    except httpx.HTTPStatusError as e:
        return None, None, f"HTTP {e.response.status_code}"
    except httpx.RequestError as e:
        return None, None, f"Request failed: {e}"
    except Exception as e:
        return None, None, str(e)


# ─── Provider class ───────────────────────────────────────────────────────────


class LocalWebExtractProvider(WebSearchProvider):
    """Zero-API-key, local-only web content extraction provider.

    Fetches pages directly via httpx and extracts content using
    trafilatura / readability / BeautifulSoup / PyMuPDF.  Requires
    no external services.
    """

    @property
    def name(self) -> str:
        return "local"

    @property
    def display_name(self) -> str:
        return "Local (trafilatura)"

    def is_available(self) -> bool:
        """Return True when httpx is available (stdlib-level dep).

        The actual extraction libraries (trafilatura, readability, bs4,
        PyMuPDF) are treated as optional upgrades — if trafilatura is
        not installed, the provider falls back gracefully through
        readability → bs4 → raw text.
        """
        try:
            import httpx  # noqa: F401
            return True
        except ImportError:
            return False

    def supports_search(self) -> bool:
        return False

    def supports_extract(self) -> bool:
        return True

    async def extract(
        self, urls: List[str], **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """Fetch and extract content from URLs using local libraries.

        Returns the standard extract result list shape.
        """
        results: list[Dict[str, Any]] = []

        for url in urls:
            result: Dict[str, Any] = {
                "url": url,
                "title": "",
                "content": "",
                "raw_content": "",
                "metadata": {},
            }

            try:
                html, pdf_bytes, error = await _fetch_url(url)

                if error:
                    result["error"] = error
                    results.append(result)
                    continue

                # PDF branch
                if pdf_bytes is not None:
                    text = _extract_pdf(pdf_bytes)
                    if text:
                        result["content"] = text
                        result["raw_content"] = text
                        result["metadata"]["format"] = "pdf"
                    else:
                        result["error"] = "Failed to extract PDF content"
                    results.append(result)
                    continue

                if not html:
                    result["error"] = "Empty response"
                    results.append(result)
                    continue

                # Extract title from HTML
                title = _extract_title(html)
                result["title"] = title or ""
                result["metadata"]["title"] = title or ""

                # Extract content
                content = _extract_content(html, url)
                if content:
                    result["content"] = content
                    result["raw_content"] = content
                    result["metadata"]["chars"] = len(content)
                else:
                    result["error"] = "No extractable content found"

            except Exception as exc:
                logger.warning("Local extract failed for %s: %s", url, exc)
                result["error"] = str(exc)

            results.append(result)

        return results

    def get_setup_schema(self) -> Dict[str, Any]:
        return {
            "name": "Local (trafilatura)",
            "badge": "free · no key · extract only",
            "tag": (
                "Extract web content using local Python libraries "
                "(trafilatura, readability-lxml, BeautifulSoup, PyMuPDF) — "
                "no API key required (pair with any search backend)"
            ),
            "env_vars": [],
            "post_setup": "local",
        }


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _extract_title(html: str) -> Optional[str]:
    """Extract <title> from HTML."""
    match = re.search(
        r"<title[^>]*>(.*?)</title\s*>", html, re.IGNORECASE | re.DOTALL
    )
    if match:
        title = match.group(1).strip()
        # Decode common HTML entities
        title = title.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        title = title.replace("&quot;", '"').replace("&#39;", "'")
        return title if title else None
    return None


# ─── Post-setup helper: pip install the optional deps ─────────────────────────


def run_local_post_setup() -> str:
    """Called after the user selects 'local' in ``hermes tools``.

    Returns a message shown to the user.
    """
    missing = []
    for pkg in ("trafilatura", "readability-lxml", "beautifulsoup4", "PyMuPDF"):
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            missing.append(pkg)

    if not missing:
        return "All local extraction packages are already installed ✓"

    return (
        "Run the following to install optional extraction packages:\n\n"
        f"  pip install {' '.join(missing)}\n\n"
        "Or install all at once:\n\n"
        "  pip install trafilatura readability-lxml beautifulsoup4 PyMuPDF"
    )