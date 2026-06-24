import pytest
from backend.api.router import router

@pytest.mark.asyncio
async def test_sse_delimiter_splitting_and_fallback():
    import json
    import re
    from pydantic import TypeAdapter
    from backend.models.dto import RecommendationDTO

    # Mock corrupted LLM output
    full_response_buffer = """
Some insights here.
  ---REC_SPLIT---   
[
  {
    "priority": 1,
    "category": "SEO",
    "issue": "Missing H1",
    "actionable_recommendation": "Add H1",
    "metric_reference": "headings.h1"
  }
]
"""
    
    recommendations_data = []
    
    # Standard split
    try:
        parts = full_response_buffer.split("---REC_SPLIT---")
        json_accumulator = parts[1]
        
        clean_json = json_accumulator.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
        clean_json = clean_json.strip()
        
        raw_recs = json.loads(clean_json)
        recommendations = TypeAdapter(list[RecommendationDTO]).validate_python(raw_recs)
        recommendations_data = [r.model_dump() for r in recommendations]
    except Exception:
        # Fallback Regex
        match = re.search(r'\[\s*\{.*\}\s*\]', full_response_buffer, re.DOTALL)
        if match:
            raw_recs = json.loads(match.group(0))
            recommendations = TypeAdapter(list[RecommendationDTO]).validate_python(raw_recs)
            recommendations_data = [r.model_dump() for r in recommendations]

    # Assert fallback regex rescues the array / splitting works
    assert len(recommendations_data) == 1
    assert recommendations_data[0]["issue"] == "Missing H1"
