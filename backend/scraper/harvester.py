import re
import sys
import httpx
from urllib.parse import urlparse
from selectolax.parser import HTMLParser
from fastapi import HTTPException
from backend.models.dto import (
    ScrapedMetricsDTO,
    HeadingsDTO,
    LinksDTO,
    ImagesDTO,
    MetadataDTO,
)

def _log(msg: str):
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()

# Threshold to decide if the page is JS-rendered (empty shell)
_MIN_WORD_COUNT = 5

class SelectolaxPageHarvester:

    async def harvest(self, url: str) -> tuple[ScrapedMetricsDTO, str]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 AuditorOne/1.0"
        }

        # Phase 1: Fast fetch with httpx
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
                response = await client.get(url, headers=headers)
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Harvester Error: Request timed out.")
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Harvester Error: Request failed - {str(e)}")

        if "text/html" not in response.headers.get("Content-Type", "").lower():
            raise HTTPException(status_code=415, detail="Harvester Error: Unsupported Media Type. Expected text/html.")

        html_content = response.text
        metrics = self._extract_metrics(html_content, url)

        # Phase 2: If content is thin, the page is likely JS-rendered — use Playwright
        is_thin = (
            metrics.word_count < _MIN_WORD_COUNT
            and metrics.headings.h1 == 0
            and metrics.headings.h2 == 0
            and metrics.links.internal == 0
            and metrics.links.external == 0
        )

        if is_thin:
            _log(f"[HARVESTER] Thin content detected (word_count={metrics.word_count}). Falling back to Playwright...")
            rendered_html = await self._render_with_playwright(url)
            if rendered_html:
                html_content = rendered_html
                metrics = self._extract_metrics(html_content, url)
                _log(f"[HARVESTER] Playwright rendered — word_count={metrics.word_count}, h1={metrics.headings.h1}")
            else:
                _log("[HARVESTER] Playwright fallback failed, using httpx results")

        return metrics, html_content

    async def _render_with_playwright(self, url: str) -> str | None:
        """Launch headless Chromium, render page content, return HTML after JS hydration."""
        from playwright.async_api import async_playwright, TimeoutError as PWTimeout

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                               "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 AuditorOne/1.0",
                    viewport={"width": 1280, "height": 720},
                )
                page = await context.new_page()

                # domcontentloaded fires once HTML is parsed — fast even for SPAs
                # Catch goto timeout so the browser stays alive and we can still grab the DOM
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                except PWTimeout:
                    _log("[HARVESTER] goto domcontentloaded timeout — grabbing partial DOM")

                # Poll until React/Vue has injected visible text into the body (max 12s)
                try:
                    await page.wait_for_function(
                        "document.body && document.body.innerText.trim().length > 100",
                        timeout=12000,
                    )
                except PWTimeout:
                    # Partial hydration — still better than the empty httpx shell
                    _log("[HARVESTER] hydration wait timeout — proceeding with partial DOM")

                html = await page.content()
                await browser.close()
                return html

        except Exception as e:
            _log(f"[HARVESTER] Playwright hard error: {e}")
            return None


    def _extract_metrics(self, html_content: str, url: str) -> ScrapedMetricsDTO:
        """Parse HTML with selectolax and extract all deterministic metrics."""
        tree = HTMLParser(html_content)

        # Remove script/style/noscript before text extraction
        for tag in tree.css("script, style, noscript"):
            tag.decompose()

        visible_text = tree.body.text() if tree.body else ""
        word_count = len(visible_text.split())

        # Headings
        headings_h1 = len(tree.css("h1"))
        headings_h2 = len(tree.css("h2"))
        headings_h3 = len(tree.css("h3"))

        # Links
        base_netloc = urlparse(url).netloc
        internal_links = 0
        external_links = 0
        for a_tag in tree.css("a[href]"):
            attrs = a_tag.attributes or {}
            href = (attrs.get("href") or "").strip()
            if not href or href.startswith("javascript:") or href.startswith("mailto:") or href.startswith("tel:"):
                continue

            parsed_href = urlparse(href)
            if not parsed_href.netloc or parsed_href.netloc == base_netloc:
                internal_links += 1
            else:
                external_links += 1

        # CTAs
        cta_count = len(tree.css('button, input[type="submit"], a.btn, a.button'))
        cta_regex = re.compile(r"(?i)(get started|book|contact|demo|sign up|buy|try|download)")
        for a_tag in tree.css("a"):
            attrs = a_tag.attributes or {}
            class_attr = attrs.get("class") or ""
            if "btn" not in class_attr and "button" not in class_attr:
                text = a_tag.text(strip=True)
                if cta_regex.search(text):
                    cta_count += 1

        # Images
        img_tags = tree.css("img")
        total_images = len(img_tags)
        missing_alt = sum(1 for img in img_tags if not ((img.attributes or {}).get("alt") or "").strip())
        missing_alt_percentage = (missing_alt / total_images * 100) if total_images > 0 else 0.0

        # Metadata
        # Re-parse fresh tree for metadata since we decomposed script/style above
        meta_tree = HTMLParser(html_content)
        title_tag = meta_tree.css_first("title")
        title = title_tag.text(strip=True) if title_tag else None

        desc_tag = meta_tree.css_first('meta[name="description"]')
        description = ((desc_tag.attributes or {}).get("content") or "").strip() if desc_tag else None

        return ScrapedMetricsDTO(
            word_count=word_count,
            headings=HeadingsDTO(h1=headings_h1, h2=headings_h2, h3=headings_h3),
            links=LinksDTO(internal=internal_links, external=external_links),
            cta_count=cta_count,
            images=ImagesDTO(
                total=total_images,
                missing_alt=missing_alt,
                missing_alt_percentage=missing_alt_percentage
            ),
            metadata=MetadataDTO(title=title, description=description)
        )

