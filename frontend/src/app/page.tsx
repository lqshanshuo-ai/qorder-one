"use client";

import { useEffect, useState } from "react";
import { pipelineApi, analyticsApi } from "@/lib/api";
import type { PipelineStatus, AnalyticsSummary } from "@/types";

export default function DashboardPage() {
  const [pipeline, setPipeline] = useState<PipelineStatus | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      pipelineApi.status().catch(() => null),
      analyticsApi.summary().catch(() => null),
    ]).then(([p, a]) => {
      setPipeline(p);
      setAnalytics(a);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="text-[var(--text-secondary)]">Loading...</div>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Dashboard</h2>

      {/* Pipeline Status */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard label="Today's Topics" value={pipeline?.topics_today ?? 0} color="var(--accent)" />
        <StatCard label="Confirmed" value={pipeline?.confirmed_topics ?? 0} color="var(--accent-green)" />
        <StatCard label="Content Done" value={pipeline?.content_generated ?? 0} color="var(--accent-yellow)" />
        <StatCard label="Videos Done" value={pipeline?.videos_generated ?? 0} color="var(--accent)" />
      </div>

      {/* Analytics Summary */}
      <h3 className="text-lg font-semibold mb-4">Overall Analytics</h3>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
        <StatCard label="Total Views" value={analytics?.total_views ?? 0} />
        <StatCard label="Total Likes" value={analytics?.total_likes ?? 0} />
        <StatCard label="Comments" value={analytics?.total_comments ?? 0} />
        <StatCard label="Shares" value={analytics?.total_shares ?? 0} />
        <StatCard
          label="Avg Engagement"
          value={`${((analytics?.avg_engagement_rate ?? 0) * 100).toFixed(2)}%`}
          color="var(--accent-green)"
        />
      </div>

      {/* Quick Actions */}
      <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
      <div className="flex gap-3">
        <RunPipelineButton />
        <a href="/topics" className="btn btn-outline">View Topics</a>
        <a href="/videos" className="btn btn-outline">View Videos</a>
      </div>

      {pipeline?.last_crawl_time && (
        <p className="text-xs text-[var(--text-secondary)] mt-4">
          Last crawl: {new Date(pipeline.last_crawl_time).toLocaleString("zh-CN")}
        </p>
      )}
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: string | number; color?: string }) {
  return (
    <div className="card">
      <p className="text-xs text-[var(--text-secondary)] mb-1">{label}</p>
      <p className="text-2xl font-bold" style={color ? { color } : undefined}>
        {typeof value === "number" ? value.toLocaleString() : value}
      </p>
    </div>
  );
}

function RunPipelineButton() {
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<string | null>(null);

  const handleRun = async () => {
    setRunning(true);
    setResult(null);
    try {
      const res = await pipelineApi.run();
      setResult(`Crawled ${res.crawled_items} items, selected ${res.candidate_topics} topics`);
    } catch (e: any) {
      setResult(`Error: ${e.message}`);
    }
    setRunning(false);
  };

  return (
    <div>
      <button className="btn btn-primary" onClick={handleRun} disabled={running}>
        {running ? "Running..." : "Run Pipeline"}
      </button>
      {result && <p className="text-xs text-[var(--text-secondary)] mt-2">{result}</p>}
    </div>
  );
}
