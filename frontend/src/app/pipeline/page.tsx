"use client";

import { useEffect, useState } from "react";
import { pipelineApi, crawlApi, notificationsApi } from "@/lib/api";
import type { PipelineStatus } from "@/types";

export default function PipelinePage() {
  const [status, setStatus] = useState<PipelineStatus | null>(null);
  const [log, setLog] = useState<string[]>([]);
  const [running, setRunning] = useState(false);

  const fetchStatus = async () => {
    try {
      const s = await pipelineApi.status();
      setStatus(s);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => { fetchStatus(); }, []);

  const addLog = (msg: string) => setLog((prev) => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);

  const handleRunCrawl = async () => {
    setRunning(true);
    addLog("Starting crawl...");
    try {
      const result = await crawlApi.run();
      addLog(`Crawl complete: ${result.items_count} items from ${result.sources.join(", ")}`);
      fetchStatus();
    } catch (e: any) {
      addLog(`Crawl error: ${e.message}`);
    }
    setRunning(false);
  };

  const handleRunFull = async () => {
    setRunning(true);
    addLog("Running full pipeline (crawl + topic selection)...");
    try {
      const result = await pipelineApi.run();
      addLog(`Pipeline complete: ${result.crawled_items} items, ${result.candidate_topics} topics`);
      result.topics.forEach((t) => addLog(`  Topic: ${t.title}`));
      fetchStatus();
    } catch (e: any) {
      addLog(`Pipeline error: ${e.message}`);
    }
    setRunning(false);
  };

  const handlePushTopics = async () => {
    addLog("Pushing topics to DingDing...");
    try {
      const result = await notificationsApi.sendTopics();
      addLog(`Push result: ${result.status}, ${result.topics_count} topics sent`);
    } catch (e: any) {
      addLog(`Push error: ${e.message}`);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Pipeline Control</h2>

      {/* Status Overview */}
      {status && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
          <StatusItem label="Crawl Status" value={status.crawl_status} />
          <StatusItem label="Topics Today" value={status.topics_today} />
          <StatusItem label="Confirmed" value={status.confirmed_topics} />
          <StatusItem label="Content Done" value={status.content_generated} />
          <StatusItem label="Videos Done" value={status.videos_generated} />
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3 mb-6">
        <button className="btn btn-outline" onClick={handleRunCrawl} disabled={running}>
          {running ? "Running..." : "Run Crawl Only"}
        </button>
        <button className="btn btn-primary" onClick={handleRunFull} disabled={running}>
          {running ? "Running..." : "Run Full Pipeline"}
        </button>
        <button className="btn btn-outline" onClick={handlePushTopics}>
          Push Topics to DingDing
        </button>
      </div>

      {/* Log Output */}
      <h3 className="text-lg font-semibold mb-3">Activity Log</h3>
      <div className="card bg-black/30 font-mono text-sm max-h-96 overflow-y-auto">
        {log.length === 0 ? (
          <p className="text-[var(--text-secondary)]">No activity yet. Run a pipeline step to see logs.</p>
        ) : (
          log.map((line, i) => (
            <p key={i} className="text-[var(--accent)] mb-1">{line}</p>
          ))
        )}
      </div>
    </div>
  );
}

function StatusItem({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="card text-center">
      <p className="text-xs text-[var(--text-secondary)] mb-1">{label}</p>
      <p className="text-xl font-bold">{value}</p>
    </div>
  );
}
