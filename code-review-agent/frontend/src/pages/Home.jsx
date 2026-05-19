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

  const cards = [
    {
      title: "PR Review",
      desc: "Review pull request diffs for bugs, security issues, and best practices.",
      route: "/review/pr", label: "Review a PR",
    },
    {
      title: "Commit Review",
      desc: "Analyze individual commits for quality and correctness.",
      route: "/review/commit", label: "Review a Commit",
    },
    {
      title: "Issue Analysis",
      desc: "Analyze GitHub issues for clarity, priority, and reproduction steps.",
      route: "/review/issue", label: "Analyze an Issue",
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 32, fontWeight: 800 }}>Code Review AI Agent</h1>
        <p className="text-muted mt-8" style={{ fontSize: 16 }}>
          Instant AI-powered reviews for GitHub PRs, commits, and issues.
        </p>
      </div>

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

      <div className="flex gap-16" style={{ flexWrap: "wrap" }}>
        {cards.map((card) => (
          <div key={card.route} className="card" style={{ flex: 1, minWidth: 220 }}>
            <div style={{ fontSize: 28, marginBottom: 12 }}>{card.icon}</div>
            <h3 style={{ fontWeight: 700, marginBottom: 6 }}>{card.title}</h3>
            <p className="text-muted text-sm" style={{ marginBottom: 16 }}>{card.desc}</p>
            <button className="btn btn-primary" onClick={() => navigate(card.route)}>
              {card.label}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}