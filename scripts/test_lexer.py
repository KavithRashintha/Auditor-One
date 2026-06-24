from backend.scraper.dom_lexer import DOMLexer

html = """
<html>
<head><style>.hidden { display: none; }</style></head>
<body>
    <nav>
        <a href="/home">Home</a>
    </nav>
    <div id="cookie-banner">Accept cookies</div>
    <main>
        <h1>Welcome to Example</h1>
        <p>This is a paragraph with a <a href="https://example.com/link">link</a>.</p>
        <div>
            <h2>Subsection</h2>
            <img src="img.jpg" alt="An example image">
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
        </div>
        <script>console.log("hello");</script>
    </main>
    <footer>Copyright 2026</footer>
</body>
</html>
"""

lexer = DOMLexer()
markdown = lexer.lex(html)
print(markdown)
