import pytest
import time
import httpx
from unittest.mock import patch
from backend.scraper.harvester import SelectolaxPageHarvester

@pytest.mark.asyncio
async def test_selectolax_speed_and_accuracy(mock_html):
    harvester = SelectolaxPageHarvester()
    url = "https://example.com"
    
    # Mock httpx response
    class MockResponse:
        def __init__(self, text):
            self.text = text
            self.headers = {"Content-Type": "text/html"}

    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = MockResponse(mock_html)
        
        start_time = time.perf_counter()
        metrics, raw_html = await harvester.harvest(url)
        end_time = time.perf_counter()

    duration_ms = (end_time - start_time) * 1000

    # 1. Assert speed
    assert duration_ms < 50, f"Harvester took too long: {duration_ms}ms"
    
    # 2. Assert accuracy
    assert metrics.cta_count == 3
    assert metrics.links.internal == 2
    assert metrics.links.external == 1
    assert metrics.images.total == 2
    assert metrics.images.missing_alt == 1
    assert metrics.metadata.title == "Mock Agency Page"
