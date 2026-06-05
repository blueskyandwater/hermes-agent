"""Local web content extraction plugin — bundled, auto-loaded.

Backed by trafilatura / readability-lxml / BeautifulSoup / PyMuPDF.
No API key required, all processing is local.
"""

from __future__ import annotations

from plugins.web.local.provider import LocalWebExtractProvider, run_local_post_setup


def register(ctx) -> None:
    """Register the local extract provider with the plugin context."""
    ctx.register_web_search_provider(LocalWebExtractProvider())