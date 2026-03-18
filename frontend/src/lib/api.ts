const API_BASE = "/api";

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }
  return res.json();
}

// Crawl
export const crawlApi = {
  run: (source?: string) =>
    fetchApi<{ status: string; items_count: number; sources: string[] }>(
      `/crawl/run${source ? `?source=${source}` : ""}`,
      { method: "POST" }
    ),
  listItems: (params?: { source?: string; date?: string; limit?: number }) => {
    const qs = new URLSearchParams();
    if (params?.source) qs.set("source", params.source);
    if (params?.date) qs.set("date", params.date);
    if (params?.limit) qs.set("limit", String(params.limit));
    const q = qs.toString();
    return fetchApi<import("@/types").CrawledItem[]>(`/crawl/items${q ? `?${q}` : ""}`);
  },
  sources: () => fetchApi<{ sources: string[] }>("/crawl/sources"),
};

// Topics
export const topicsApi = {
  list: (params?: { status?: string; category?: string }) => {
    const qs = new URLSearchParams();
    if (params?.status) qs.set("status", params.status);
    if (params?.category) qs.set("category", params.category);
    const q = qs.toString();
    return fetchApi<import("@/types").Topic[]>(`/topics${q ? `?${q}` : ""}`);
  },
  candidates: () => fetchApi<import("@/types").Topic[]>("/topics/candidates"),
  get: (id: string) => fetchApi<import("@/types").Topic>(`/topics/${id}`),
  create: (data: { title: string; description?: string; category: string; priority?: number }) =>
    fetchApi<import("@/types").Topic>("/topics", { method: "POST", body: JSON.stringify(data) }),
  confirm: (id: string) =>
    fetchApi<import("@/types").Topic>(`/topics/${id}/confirm`, { method: "PATCH" }),
  reject: (id: string) =>
    fetchApi<import("@/types").Topic>(`/topics/${id}/reject`, { method: "PATCH" }),
  confirmBatch: (topicIds: string[]) =>
    fetchApi<import("@/types").Topic[]>("/topics/confirm-batch", {
      method: "POST",
      body: JSON.stringify({ topic_ids: topicIds }),
    }),
};

// Content
export const contentApi = {
  generate: (topicId: string, durationSeconds?: number) =>
    fetchApi<import("@/types").ContentResult>(`/content/generate/${topicId}`, {
      method: "POST",
      body: JSON.stringify({ duration_seconds: durationSeconds || 75 }),
    }),
};

// Videos
export const videosApi = {
  list: (status?: string) => {
    const q = status ? `?status=${status}` : "";
    return fetchApi<import("@/types").Video[]>(`/videos${q}`);
  },
  get: (id: string) => fetchApi<import("@/types").Video>(`/videos/${id}`),
  generate: (scriptId: string) =>
    fetchApi<{ video_id: string; status: string; file_path: string }>(
      `/videos/generate/${scriptId}`,
      { method: "POST" }
    ),
};

// Pipeline
export const pipelineApi = {
  status: () => fetchApi<import("@/types").PipelineStatus>("/pipeline/status"),
  run: () =>
    fetchApi<{ crawled_items: number; candidate_topics: number; topics: { id: string; title: string }[] }>(
      "/pipeline/run",
      { method: "POST" }
    ),
};

// Analytics
export const analyticsApi = {
  summary: () => fetchApi<import("@/types").AnalyticsSummary>("/analytics/summary"),
  record: (data: {
    publishing_id: string;
    views: number;
    likes: number;
    comments: number;
    shares: number;
    notes?: string;
  }) =>
    fetchApi<import("@/types").AnalyticsRecord>("/analytics/record", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

// Publishing
export const publishingApi = {
  prepare: (videoId: string, platforms?: string[]) =>
    fetchApi<import("@/types").Publishing[]>(
      `/publishing/prepare/${videoId}${platforms ? `?${platforms.map((p) => `platforms=${p}`).join("&")}` : ""}`,
      { method: "POST" }
    ),
  list: (params?: { platform?: string; status?: string }) => {
    const qs = new URLSearchParams();
    if (params?.platform) qs.set("platform", params.platform);
    if (params?.status) qs.set("status", params.status);
    const q = qs.toString();
    return fetchApi<import("@/types").Publishing[]>(`/publishing${q ? `?${q}` : ""}`);
  },
};

// Notifications
export const notificationsApi = {
  sendTopics: () =>
    fetchApi<{ status: string; topics_count: number }>("/notifications/send-topics", {
      method: "POST",
    }),
};
