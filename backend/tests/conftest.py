import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_html():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Mock Agency Page</title>
        <meta name="description" content="A mock page for testing harvester.">
    </head>
    <body>
        <h1>Primary Headline</h1>
        <h2>Secondary Section</h2>
        
        <!-- CTAs (Buttons) -->
        <button id="btn1">Click Me</button>
        <a class="btn" href="/pricing">View Pricing</a>
        <a href="/demo">Book a Demo</a> <!-- 'demo' is in cta_regex -->
        
        <!-- Internal / External Links -->
        <!-- 'demo' and 'pricing' are internal links -->
        <a href="https://external-domain.com/link">External Link</a>
        
        <!-- Images: 1 missing alt, 1 with alt -->
        <img src="logo.png" alt="Company Logo">
        <img src="hero-bg.jpg">
        
    </body>
    </html>
    """
