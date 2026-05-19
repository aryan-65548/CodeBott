import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { healthCheck } from "../api/client";

export default function Home() {
  const [status, setStatus] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    healthCheck()
      .then(res => setStatus(res.data))
      .catch(() => setStatus({ status: "offline" }));
  }, []);

  return (
    <div>
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 32, fontWeight: 800 }}>Code Review AI Agent</h1>
        <p className="text-muted mt-8" style={{ fontSize: 16 }}>
          Instant AI-powered reviews for GitHub PRs, commits, and issues.
        </p>
      </div>

      {/* Status */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="flex items-center gap-8">
          <div style={{
            width: 8, height: 8, borderRadius: "50%",
            background: status?.status === "ok" ? "#3fb950" : "#f85149",
          }} />
          <span className="text-sm">
            API {status?.status === "ok" ? "online" : "offline"}
            {status?.model && ` — ${status.model}`}
          </span>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="flex gap-16" style={{ flexWrap: "wrap" }}>
        <div className="card" style={{ flex: 1, minWidth: 220 }}>
          <div style={{ fontSize: 28, marginBottom: 12 }}></div>
          <h3 style={{ fontWeight: 700, marginBottom: 6 }}>PR Review</h3>
          <p className="text-muted text-sm" style={{ marginBottom: 16 }}>
            Review pull request diffs for bugs, security issues, and best practices.
          </p>
          <button className="btn btn-primary" onClick={() => navigate("/review/pr")}>
            Review a PR
          </button>
        </div>

        <div className="card" style={{ flex: 1, minWidth: 220, opacity: 0.6 }}>
          <div style={{ fontSize: 28, marginBottom: 12 }}></div>
          <h3 style={{ fontWeight: 700, marginBottom: 6 }}>Commit Review</h3>
          <p className="text-muted text-sm" style={{ marginBottom: 16 }}>
            Analyze individual commits for quality and correctness.
          </p>
          <button className="btn btn-secondary" disabled>Coming soon</button>
        </div>

        <div className="card" style={{ flex: 1, minWidth: 220, opacity: 0.6 }}>
          <div style={{ fontSize: 28, marginBottom: 12 }}></div>
          <h3 style={{ fontWeight: 700, marginBottom: 6 }}>Issue Analysis</h3>
          <p className="text-muted text-sm" style={{ marginBottom: 16 }}>
            Analyze GitHub issues for clarity, priority, and reproduction steps.
          </p>
          <button className="btn btn-secondary" disabled>Coming soon</button>
        </div>
      </div>
    </div>
  );
}