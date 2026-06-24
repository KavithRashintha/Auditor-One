from pydantic import BaseModel, ConfigDict
from typing import Optional

class HeadingsDTO(BaseModel):
    h1: int
    h2: int
    h3: int

    model_config = ConfigDict(strict=True)

class LinksDTO(BaseModel):
    internal: int
    external: int

    model_config = ConfigDict(strict=True)

class ImagesDTO(BaseModel):
    total: int
    missing_alt: int
    missing_alt_percentage: float

    model_config = ConfigDict(strict=True)

class MetadataDTO(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    title_length: Optional[int] = None       # chars; SEO ideal: 30-60
    description_length: Optional[int] = None # chars; SEO ideal: 70-160

    model_config = ConfigDict(strict=True)

class ScrapedMetricsDTO(BaseModel):
    word_count: int
    headings: HeadingsDTO
    links: LinksDTO
    cta_count: int
    images: ImagesDTO
    metadata: MetadataDTO

    model_config = ConfigDict(strict=True)

class RecommendationDTO(BaseModel):
    priority: int
    category: str
    issue: str
    actionable_recommendation: str
    metric_reference: str

    model_config = ConfigDict(strict=True)

class AuditRequest(BaseModel):
    url: str

    model_config = ConfigDict(strict=True)
