export interface Topic {
  id: string;
  title: string;
  description: string;
  category: string;
  priority: number;
  status: "candidate" | "confirmed" | "in_progress" | "completed" | "rejected";
  reason: string;
  source_item_id: string | null;
  confirmation_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface CrawledItem {
  id: string;
  source: string;
  source_url: string;
  title: string;
  summary: string;
  category_tags: string[] | null;
  popularity_score: number;
  crawl_date: string;
  created_at: string;
}

export interface ContentResult {
  topic_id: string;
  content_id: string;
  script_id: string;
  title: string;
  segments_count: number;
  duration: number;
}

export interface Video {
  id: string;
  topic_id: string;
  script_id: string;
  file_path: string;
  cover_image_path: string;
  duration_seconds: number;
  resolution: string;
  file_size_mb: number;
  status: "pending" | "generating" | "completed" | "failed";
  style_template: string;
  created_at: string;
}

export interface Publishing {
  id: string;
  video_id: string;
  platform: "douyin" | "xiaohongshu";
  caption: string;
  hashtags: string[] | null;
  cover_image_path: string;
  status: "pending" | "published" | "failed";
  published_at: string | null;
  created_at: string;
}

export interface AnalyticsRecord {
  id: string;
  publishing_id: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  engagement_rate: number;
  recorded_at: string;
  notes: string;
}

export interface PipelineStatus {
  crawl_status: string;
  topics_today: number;
  confirmed_topics: number;
  content_generated: number;
  videos_generated: number;
  last_crawl_time: string | null;
}

export interface AnalyticsSummary {
  total_views: number;
  total_likes: number;
  total_comments: number;
  total_shares: number;
  avg_engagement_rate: number;
  total_records: number;
}
