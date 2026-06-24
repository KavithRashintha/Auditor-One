import re
from selectolax.parser import HTMLParser, Node

class DOMLexer:
    def lex(self, html: str) -> str:
        tree = HTMLParser(html)
        
        bloat_selectors = [
            "script", "style", "noscript", "svg", "canvas", "iframe",
            "footer", "header", "nav", "#cookie-banner"
        ]
        for selector in bloat_selectors:
            for tag in tree.css(selector):
                tag.decompose()

        def _traverse(node: Node) -> str:
            res = ""
            child = node.child
            while child:
                if child.tag == "-text":
                    # For text nodes, collapse whitespace
                    content = child.text_content or ""
                    text = re.sub(r'\s+', ' ', content).strip()
                    if text:
                        res += text + " "
                elif child.tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                    level = int(child.tag[1])
                    text = _traverse(child).strip()
                    if text:
                        res += f"\n\n{'#' * level} {text}\n\n"
                elif child.tag == "a":
                    attrs = child.attributes or {}
                    href = attrs.get("href") or ""
                    text = _traverse(child).strip()
                    if text and href:
                        res += f" [{text}]({href}) "
                    elif text:
                        res += f" {text} "
                elif child.tag == "img":
                    attrs = child.attributes or {}
                    src = attrs.get("src") or ""
                    alt = attrs.get("alt") or ""
                    if src:
                        res += f" ![{alt}]({src}) "
                elif child.tag in ["p", "div", "li", "section", "article"]:
                    text = _traverse(child).strip()
                    if text:
                        res += f"\n{text}\n"
                else:
                    # For other tags (span, strong, em, etc.), just process children
                    res += _traverse(child)
                
                child = child.next
            return res

        if tree.body:
            markdown = _traverse(tree.body)
        elif tree.root:
            markdown = _traverse(tree.root)
        else:
            markdown = ""

        # Clean up multiple consecutive newlines and spaces
        markdown = re.sub(r' {2,}', ' ', markdown)
        markdown = re.sub(r'\n{3,}', '\n\n', markdown).strip()

        # Token hard-cap at 12800 characters
        if len(markdown) > 12800:
            truncated = markdown[:12800]
            last_break = truncated.rfind('\n\n')
            if last_break != -1:
                markdown = truncated[:last_break]
            else:
                markdown = truncated
            
            markdown += "\n\n[AUDIT SYSTEM NOTICE: DOM TRUNCATED FOR LLM CONTEXT WINDOW LIMITS. METRICS REMAIN FACTUALLY ABSOLUTE.]"

        return markdown
