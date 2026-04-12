"""Google Search module — reliable search using DuckDuckGo API."""

import requests


def google_search(query, num_results=6):
    """
    Search using DuckDuckGo Instant Answer API (free, no API key).
    Falls back to DuckDuckGo HTML search for full results.

    Returns:
        list of dicts: [{"title": str, "url": str}, ...]
    """
    results = []

    try:
        results = _duckduckgo_search(query, num_results)
    except Exception as e:
        print(f"[SEARCH ERROR] {e}")

    return results


def _duckduckgo_search(query, num_results=6):
    """Search DuckDuckGo and parse results."""
    import re

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    url = "https://html.duckduckgo.com/html/"
    params = {"q": query}

    response = requests.get(url, params=params, headers=headers, timeout=10)
    response.raise_for_status()

    html = response.text
    results = []

    pattern = r'class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>'
    matches = re.findall(pattern, html, re.DOTALL)

    for href, title_html in matches[:num_results]:
        title = re.sub(r"<[^>]+>", "", title_html).strip()

        actual_url = href
        if "uddg=" in href:
            url_match = re.search(r"uddg=([^&]+)", href)
            if url_match:
                from urllib.parse import unquote
                actual_url = unquote(url_match.group(1))

        if title and actual_url:
            results.append({"title": title, "url": actual_url})

    return results