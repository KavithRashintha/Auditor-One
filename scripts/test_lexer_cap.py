from backend.scraper.dom_lexer import DOMLexer

html = "<html><body>" + ("<p>This is a paragraph.</p>\n" * 1000) + "</body></html>"

lexer = DOMLexer()
markdown = lexer.lex(html)
print(f"Length: {len(markdown)}")
print(markdown[-150:])
