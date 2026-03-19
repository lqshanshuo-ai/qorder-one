"use client";

import { useEffect, useState } from "react";
import { analyticsApi } from "@/lib/api";
import type { AnalyticsSummary } from "@/types";

export default function AnalyticsPage() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyticsApi.summary().then(setSummary).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-[var(--text-secondary)]">Loading...</p>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Analytics</h2>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
        <MetricCard label="Total Views" value={summary?.total_views ?? 0} icon="👁️" />
        <MetricCard label="Total Likes" value={summary?.total_likes ?? 0} icon="❤️" />
        <MetricCard label="Total Comments" value={summary?.total_comments ?? 0} icon="💬" />
        <MetricCard label="Total Shares" value={summary?.total_shares ?? 0} icon="🔗" />
        <MetricCard
          label="Avg Engagement Rate"
          value={`${((summary?.avg_engagement_rate ?? 0) * 100).toFixed(2)}%`}
          icon="📊"
        />
        <MetricCard label="Records" value={summary?.total_records ?? 0} icon="📝" />
      </div>

      {/* Manual Entry */}
      <h3 className="text-lg font-semibold mb-4">Record Performance</h3>
      <AnalyticsForm />

      <div className="card mt-8">
        <h3 className="text-lg font-semibold mb-2">Tips for Optimization</h3>
        <ul className="text-sm text-[var(--text-secondary)] space-y-2">
          <li>- Track performance daily for each published video</li>
          <li>- Compare engagement rates across different topic categories</li>
          <li>- Topics with higher engagement should influence future topic selection</li>
          <li>- Best posting times on Douyin: 12:00-13:00, 18:00-20:00, 21:00-23:00</li>
          <li>- Best posting times on Xiaohongshu: 7:00-9:00, 12:00-14:00, 18:00-22:00</li>
        </ul>
      </div>
    </div>
  );
}

function MetricCard({ label, value, icon }: { label: string; value: string | number; icon: string }) {
  return (
    <div className="card flex items-center gap-4">
      <span className="text-3xl">{icon}</span>
      <div>
        <p className="text-xs text-[var(--text-secondary)]">{label}</p>
        <p className="text-xl font-bold">
          {typeof value === "number" ? value.toLocaleString() : value}
        </p>
      </div>
    </div>
  );
}

function AnalyticsForm() {
  const [form, setForm] = useState({
    publishing_id: "",
    views: 0,
    likes: 0,
    comments: 0,
    shares: 0,
    notes: "",
  });
  const [message, setMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.publishing_id) {
      setMessage("Publishing ID is required");
      return;
    }
    try {
      await analyticsApi.record(form);
      setMessage("Analytics recorded successfully!");
      setForm({ publishing_id: "", views: 0, likes: 0, comments: 0, shares: 0, notes: "" });
    } catch (e: any) {
      setMessage(`Error: ${e.message}`);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="card">
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
        <div>
          <label className="text-xs text-[var(--text-secondary)] block mb-1">Publishing ID</label>
          <input
            type="text"
            value={form.publishing_id}
            onChange={(e) => setForm({ ...form, publishing_id: e.target.value })}
            className="w-full px-3 py-2 rounded-lg bg-[var(--background)] border border-[var(--card-border)] text-sm"
            placeholder="Enter publishing ID"
          />
        </div>
        <div>
          <label className="text-xs text-[var(--text-secondary)] block mb-1">Views</label>
          <input
            type="number"
            value={form.views}
            onChange={(e) => setForm({ ...form, views: Number(e.target.value) })}
            className="w-full px-3 py-2 rounded-lg bg-[var(--background)] border border-[var(--card-border)] text-sm"
          />
        </div>
        <div>
          <label className="text-xs text-[var(--text-secondary)] block mb-1">Likes</label>
          <input
            type="number"
            value={form.likes}
            onChange={(e) => setForm({ ...form, likes: Number(e.target.value) })}
            className="w-full px-3 py-2 rounded-lg bg-[var(--background)] border border-[var(--card-border)] text-sm"
          />
        </div>
        <div>
          <label className="text-xs text-[var(--text-secondary)] block mb-1">Comments</label>
          <input
            type="number"
            value={form.comments}
            onChange={(e) => setForm({ ...form, comments: Number(e.target.value) })}
            className="w-full px-3 py-2 rounded-lg bg-[var(--background)] border border-[var(--card-border)] text-sm"
          />
        </div>
        <div>
          <label className="text-xs text-[var(--text-secondary)] block mb-1">Shares</label>
          <input
            type="number"
            value={form.shares}
            onChange={(e) => setForm({ ...form, shares: Number(e.target.value) })}
            className="w-full px-3 py-2 rounded-lg bg-[var(--background)] border border-[var(--card-border)] text-sm"
          />
        </div>
        <div>
          <label className="text-xs text-[var(--text-secondary)] block mb-1">Notes</label>
          <input
            type="text"
            value={form.notes}
            onChange={(e) => setForm({ ...form, notes: e.target.value })}
            className="w-full px-3 py-2 rounded-lg bg-[var(--background)] border border-[var(--card-border)] text-sm"
            placeholder="Optional notes"
          />
        </div>
      </div>
      <button type="submit" className="btn btn-primary">Record Analytics</button>
      {message && <p className="text-xs mt-2 text-[var(--text-secondary)]">{message}</p>}
    </form>
  );
}
