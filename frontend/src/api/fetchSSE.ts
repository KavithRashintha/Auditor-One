import type { ScrapedMetrics, RecommendationItem } from "../types/audit";

export interface SSEHandlers {
  onMetrics: (metrics: ScrapedMetrics) => void;
  onInsightChunk: (chunk: string) => void;
  onRecommendations: (recommendations: RecommendationItem[]) => void;
  onPromptLogMeta: (traceId: string, path: string) => void;
  onError: (stage: string, message: string) => void;
  onDone: () => void;
}

export async function streamAudit(url: string, handlers: SSEHandlers): Promise<void> {
  try {
    const response = await fetch("http://localhost:8000/api/v1/audit", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      handlers.onError("ROUTER", errorData.detail || `HTTP Error ${response.status}`);
      return;
    }

    const reader = response.body?.getReader();
    if (!reader) {
      handlers.onError("NETWORK", "Response body is not readable");
      return;
    }

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      // Normalize \r\n to \n — SSE spec uses \r\n but JS split needs clean \n
      buffer += decoder.decode(value, { stream: true }).replace(/\r\n/g, "\n").replace(/\r/g, "\n");
      const parts = buffer.split("\n\n");
      buffer = parts.pop() || "";

      for (const part of parts) {
        if (!part.trim()) continue;

        const lines = part.split("\n");
        let eventType = "message";
        let dataContent = "";

        for (const line of lines) {
          if (line.startsWith("event:")) {
            eventType = line.substring(6).trim();
          } else if (line.startsWith("data:")) {
            dataContent = line.substring(5).trim();
          }
        }

        if (!dataContent) continue;

        try {
          const parsedData = JSON.parse(dataContent);
          
          switch (eventType) {
            case "metrics":
              handlers.onMetrics(parsedData);
              break;
            case "insight_chunk":
              handlers.onInsightChunk(parsedData);
              break;
            case "recommendations":
              handlers.onRecommendations(parsedData);
              break;
            case "prompt_log_meta":
              handlers.onPromptLogMeta(parsedData.trace_id, parsedData.path);
              break;
            case "error":
              handlers.onError(parsedData.stage || "UNKNOWN", parsedData.message || "An error occurred");
              break;
            case "done":
              handlers.onDone();
              return;
          }
        } catch (e) {
          console.error("Failed to parse SSE data:", dataContent, e);
        }
      }
    }
  } catch (error) {
    handlers.onError("NETWORK", error instanceof Error ? error.message : "Unknown error");
  }
}

