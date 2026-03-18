"use client";

import { useEffect, useState } from "react";
import { videosApi } from "@/lib/api";
import type { Video } from "@/types";

export default function VideosPage() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    videosApi.list().then(setVideos).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-[var(--text-secondary)]">Loading...</p>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Videos</h2>

      {videos.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-[var(--text-secondary)] mb-2">No videos generated yet.</p>
          <p className="text-sm text-[var(--text-secondary)]">
            Confirm topics and generate content to create videos.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {videos.map((video) => (
            <VideoCard key={video.id} video={video} />
          ))}
        </div>
      )}
    </div>
  );
}

function VideoCard({ video }: { video: Video }) {
  const statusColor: Record<string, string> = {
    completed: "var(--accent-green)",
    generating: "var(--accent-yellow)",
    failed: "var(--accent-red)",
    pending: "var(--text-secondary)",
  };

  return (
    <div className="card">
      {/* Cover placeholder */}
      <div className="bg-[var(--background)] rounded-lg h-48 flex items-center justify-center mb-3">
        <span className="text-4xl">🎬</span>
      </div>

      <div className="flex items-center gap-2 mb-2">
        <span
          className="w-2 h-2 rounded-full"
          style={{ background: statusColor[video.status] || "gray" }}
        />
        <span className="text-sm font-medium">{video.status}</span>
        <span className="text-xs text-[var(--text-secondary)] ml-auto">
          {video.duration_seconds}s
        </span>
      </div>

      <p className="text-xs text-[var(--text-secondary)]">
        Resolution: {video.resolution} | Size: {video.file_size_mb}MB
      </p>
      <p className="text-xs text-[var(--text-secondary)]">
        Style: {video.style_template}
      </p>
      <p className="text-xs text-[var(--text-secondary)] mt-2">
        {new Date(video.created_at).toLocaleString("zh-CN")}
      </p>

      {video.status === "completed" && (
        <a
          href={`/api/videos/${video.id}/download`}
          className="btn btn-primary w-full mt-3 text-center"
        >
          Download
        </a>
      )}
    </div>
  );
}
