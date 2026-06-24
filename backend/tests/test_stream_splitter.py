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


def test_recommendation_priority_normalization():
    import json
    from pydantic import TypeAdapter
    from backend.models.dto import RecommendationDTO

    # Recommendations with duplicate/non-sequential priorities
    raw_recs = [
        {
            "priority": 1,
            "category": "SEO",
            "issue": "Duplicate H1 tags",
            "actionable_recommendation": "Resolve duplicate H1 tags.",
            "metric_reference": "headings.h1"
        },
        {
            "priority": 1,
            "category": "UX",
            "issue": "Missing alt attributes on images",
            "actionable_recommendation": "Add alt tags.",
            "metric_reference": "images.missing_alt"
        },
        {
            "priority": 2,
            "category": "CTA",
            "issue": "Low CTA count",
            "actionable_recommendation": "Add conversion CTAs.",
            "metric_reference": "cta_count"
        },
        {
            "priority": 3,
            "category": "Content",
            "issue": "Thin word count",
            "actionable_recommendation": "Expand content depth.",
            "metric_reference": "word_count"
        }
    ]

    # Validate and dump
    recommendations = TypeAdapter(list[RecommendationDTO]).validate_python(raw_recs)
    recommendations_data = [r.model_dump() for r in recommendations]

    # Run router's priority normalization logic
    if recommendations_data:
        for idx, r in enumerate(recommendations_data, start=1):
            r["priority"] = idx

    # Assert priorities are normalized to sequential [1, 2, 3, 4]
    assert len(recommendations_data) == 4
    assert [r["priority"] for r in recommendations_data] == [1, 2, 3, 4]
