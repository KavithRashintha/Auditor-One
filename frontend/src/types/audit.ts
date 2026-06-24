export interface HeadingsMetrics {
  h1: number;
  h2: number;
  h3: number;
}

export interface LinksMetrics {
  internal: number;
  external: number;
}

export interface ImagesMetrics {
  total: number;
  missing_alt: number;
  missing_alt_percentage: number;
}

export interface MetadataMetrics {
  title: string | null;
  description: string | null;
}

export interface ScrapedMetrics {
  word_count: number;
  headings: HeadingsMetrics;
  links: LinksMetrics;
  cta_count: number;
  images: ImagesMetrics;
  metadata: MetadataMetrics;
}

export interface RecommendationItem {
  priority: number;
  category: string;
  issue: string;
  actionable_recommendation: string;
  metric_reference: string;
}

export type SSEEventMap = 
  | { event: "metrics"; data: ScrapedMetrics }
  | { event: "insight_chunk"; data: { chunk: string } }
  | { event: "recommendations"; data: RecommendationItem[] }
  | { event: "prompt_log_meta"; data: { trace_id: string; path: string } }
  | { event: "error"; data: { stage: "AUTH" | "SSRF" | "SCRAPE" | "LLM"; message: string } }
  | { event: "done"; data: Record<string, never> };
