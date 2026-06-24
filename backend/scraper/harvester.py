import re
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

class SelectolaxPageHarvester:
    async def harvest(self, url: str) -> tuple[ScrapedMetricsDTO, str]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 AuditorOne/1.0"
        }
        
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
        tree = HTMLParser(html_content)
        
        # 4. Word count
        # Remove script and style tags before extracting text to ensure accuracy
        for tag in tree.css("script, style, noscript"):
            tag.decompose()
        
        visible_text = tree.body.text() if tree.body else ""
        word_count = len(visible_text.split())

        # 5. Headings
        headings_h1 = len(tree.css("h1"))
        headings_h2 = len(tree.css("h2"))
        headings_h3 = len(tree.css("h3"))

        # 6. Links
        base_netloc = urlparse(url).netloc
        internal_links = 0
        external_links = 0
        for a_tag in tree.css("a[href]"):
            attrs = a_tag.attributes or {}
            href = (attrs.get("href") or "").strip()
            if not href or href.startswith("javascript:") or href.startswith("mailto:") or href.startswith("tel:"):
                continue
            
            parsed_href = urlparse(href)
            # Internal if it has no netloc (relative), or if the netloc matches base
            if not parsed_href.netloc or parsed_href.netloc == base_netloc:
                internal_links += 1
            else:
                external_links += 1

        # 7. CTA count
        cta_count = len(tree.css('button, input[type="submit"], a.btn, a.button'))
        
        cta_regex = re.compile(r"(?i)(get started|book|contact|demo|sign up|buy|try|download)")
        for a_tag in tree.css("a"):
            attrs = a_tag.attributes or {}
            class_attr = attrs.get("class") or ""
            if "btn" not in class_attr and "button" not in class_attr:
                text = a_tag.text(strip=True)
                if cta_regex.search(text):
                    cta_count += 1

        # 8. Images
        img_tags = tree.css("img")
        total_images = len(img_tags)
        missing_alt = sum(1 for img in img_tags if not ((img.attributes or {}).get("alt") or "").strip())
        missing_alt_percentage = (missing_alt / total_images * 100) if total_images > 0 else 0.0

        # 9. Metadata
        title_tag = tree.css_first("title")
        title = title_tag.text(strip=True) if title_tag else None

        desc_tag = tree.css_first('meta[name="description"]')
        description = ((desc_tag.attributes or {}).get("content") or "").strip() if desc_tag else None

        metrics = ScrapedMetricsDTO(
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

        return metrics, html_content
