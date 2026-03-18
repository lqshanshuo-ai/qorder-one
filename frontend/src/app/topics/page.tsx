"use client";

import { useEffect, useState } from "react";
import { topicsApi, contentApi } from "@/lib/api";
import type { Topic } from "@/types";

export default function TopicsPage() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [filter, setFilter] = useState<string>("all");
  const [loading, setLoading] = useState(true);

  const fetchTopics = async () => {
    setLoading(true);
    try {
      const params = filter !== "all" ? { status: filter } : undefined;
      const data = await topicsApi.list(params);
      setTopics(data);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => { fetchTopics(); }, [filter]);

  const handleConfirm = async (id: string) => {
    try {
      await topicsApi.confirm(id);
      fetchTopics();
    } catch (e: any) {
      alert(e.message);
    }
  };

  const handleReject = async (id: string) => {
    try {
      await topicsApi.reject(id);
      fetchTopics();
    } catch (e: any) {
      alert(e.message);
    }
  };

  const handleGenerate = async (id: string) => {
    try {
      const result = await contentApi.generate(id);
      alert(`Content generated: ${result.title} (${result.segments_count} segments, ${result.duration}s)`);
      fetchTopics();
    } catch (e: any) {
      alert(`Error: ${e.message}`);
    }
  };

  const statusFilters = ["all", "candidate", "confirmed", "in_progress", "completed", "rejected"];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Topics</h2>
        <div className="flex gap-2">
          {statusFilters.map((s) => (
            <button
              key={s}
              className={`btn ${filter === s ? "btn-primary" : "btn-outline"}`}
              onClick={() => setFilter(s)}
            >
              {s === "all" ? "All" : s.replace("_", " ")}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <p className="text-[var(--text-secondary)]">Loading...</p>
      ) : topics.length === 0 ? (
        <p className="text-[var(--text-secondary)]">No topics found</p>
      ) : (
        <div className="grid gap-4">
          {topics.map((topic) => (
            <TopicCard
              key={topic.id}
              topic={topic}
              onConfirm={handleConfirm}
              onReject={handleReject}
              onGenerate={handleGenerate}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function TopicCard({
  topic,
  onConfirm,
  onReject,
  onGenerate,
}: {
  topic: Topic;
  onConfirm: (id: string) => void;
  onReject: (id: string) => void;
  onGenerate: (id: string) => void;
}) {
  return (
    <div className="card">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <span className={`badge badge-${topic.status.replace("_", "-")}`}>{topic.status}</span>
            <span className="text-xs text-[var(--text-secondary)]">[{topic.category}]</span>
            <span className="text-xs text-[var(--text-secondary)]">
              Priority: {"⭐".repeat(Math.min(Math.ceil(topic.priority / 2), 5))}
            </span>
          </div>
          <h3 className="text-lg font-semibold mb-1">{topic.title}</h3>
          {topic.description && (
            <p className="text-sm text-[var(--text-secondary)] mb-2">{topic.description}</p>
          )}
          {topic.reason && (
            <p className="text-xs text-[var(--text-secondary)] italic">Reason: {topic.reason}</p>
          )}
        </div>
        <div className="flex gap-2 ml-4">
          {topic.status === "candidate" && (
            <>
              <button className="btn btn-success" onClick={() => onConfirm(topic.id)}>Confirm</button>
              <button className="btn btn-danger" onClick={() => onReject(topic.id)}>Reject</button>
            </>
          )}
          {topic.status === "confirmed" && (
            <button className="btn btn-primary" onClick={() => onGenerate(topic.id)}>Generate</button>
          )}
        </div>
      </div>
      <p className="text-xs text-[var(--text-secondary)] mt-3">
        Created: {new Date(topic.created_at).toLocaleString("zh-CN")}
      </p>
    </div>
  );
}
