import json
import os
from typing import Any
from backend.models.dto import ScrapedMetricsDTO

def load_rules(path: str) -> list[dict]:
    """Loads heuristic rules from a JSON file."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _get_nested_attr(obj: Any, path: str) -> Any:
    """Helper to safely fetch nested attributes from a Pydantic DTO or dict."""
    parts = path.split(".")
    current = obj
    for part in parts:
        if current is None:
            return None
        if isinstance(current, dict):
            current = current.get(part)
        else:
            current = getattr(current, part, None)
    return current

def evaluate_heuristics(metrics: ScrapedMetricsDTO, rules: list[dict]) -> list[str]:
    """
    Evaluates scraped metrics against agency heuristic rules.
    Returns a list of violated rule strings.
    """
    violated_rules = []
    
    for rule in rules:
        metric_path = rule.get("metric_path")
        condition = rule.get("condition")
        threshold = rule.get("threshold")
        rule_text = rule.get("rule")
        
        if not metric_path or not condition or not rule_text:
            continue
            
        value = _get_nested_attr(metrics, metric_path)
        
        is_violated = False
        if condition == "equals":
            is_violated = (value == threshold)
        elif condition == "greater_than":
            if value is not None and threshold is not None:
                is_violated = (value > threshold)
        elif condition == "less_than":
            if value is not None and threshold is not None:
                is_violated = (value < threshold)
        elif condition == "is_null":
            is_violated = (value is None)
            
        if is_violated:
            violated_rules.append(rule_text)
            
    return violated_rules

# Pre-load rules into memory at startup
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
AGENCY_RULES_PATH = os.path.join(_BASE_DIR, "agency_rules.json")
AGENCY_RULES = load_rules(AGENCY_RULES_PATH)
