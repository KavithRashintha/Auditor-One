from backend.models.dto import ScrapedMetricsDTO, HeadingsDTO, LinksDTO, ImagesDTO, MetadataDTO
from backend.heuristics.engine import evaluate_heuristics, AGENCY_RULES

metrics = ScrapedMetricsDTO(
    word_count=200, # thin content (< 300)
    headings=HeadingsDTO(h1=0, h2=0, h3=0), # missing h1 (equals 0)
    links=LinksDTO(internal=0, external=0), # no external (equals 0)
    cta_count=10, # excessive cta (> 8)
    images=ImagesDTO(total=10, missing_alt=6, missing_alt_percentage=60.0), # missing alt (> 50)
    metadata=MetadataDTO(title="Test", description=None) # missing meta description (is_null)
)

print(f"Loaded {len(AGENCY_RULES)} rules.")
violations = evaluate_heuristics(metrics, AGENCY_RULES)
for i, violation in enumerate(violations, 1):
    print(f"{i}. {violation}")
