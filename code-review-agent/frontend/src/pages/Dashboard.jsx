import { useState, useEffect } from "react";
import { getHistory, getStats } from "../api/client";

const TYPE_LABELS = {
  pr_review:     { label: "PR",     color: "badge-blue" },
  commit_review: { label: "Commit", color: "badge-purple" },
  issue_review:  { label: "Issue",  color: "badge-yellow" },
};

const VERDICT_LABELS = {
  approve:          { label: "Approve",          color: "badge-green" },
  request_changes:  { label: "Request Changes",  color: "badge-red" },
  needs_discussion: { label: "Needs Discussion", color: "badge-yellow" },
};

export default function Dashboard() {
  const [reviews, setReviews] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    Promise.all([getHistory(), getStats()])
      .then(([histRes, statsRes]) => {
        setReviews(histRes.data.reviews);
        setStats(statsRes.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const filtered = filter === "all"
    ? reviews
    : reviews.filter(r => r.type === filter);

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: 64 }}>
        <div className="spinner" style={{ margin: "0 auto 16px", width: 32, height: 32 }} />
        <p className="text-muted">Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 800, marginBottom: 8 }}>Dashboard</h1>
      <p className="text-muted" style={{ marginBottom: 24 }}>
        All reviews across repos
      </p>

      {/* Stats Row */}
      {stats && (
        <div className="flex gap-16" style={{ marginBottom: 24, flexWrap: "wrap" }}>
          <div className="card" style={{ flex: 1, minWidth: 140 }}>
            <div style={{ fontSize: 28, fontWeight: 800 }}>{stats.total_reviews}</div>
            <div className="text-muted text-sm">Total Reviews</div>
          </div>
          <div className="card" style={{ flex: 1, minWidth: 140 }}>
            <div style={{ fontSize: 28, fontWeight: 800 }}>{stats.average_score}</div>
            <div className="text-muted text-sm">Avg Score</div>
          </div>
          <div className="card" style={{ flex: 1, minWidth: 140 }}>
            <div style={{ fontSize: 28, fontWeight: 800, color: "#3fb950" }}>
              {stats.by_verdict?.approve || 0}
            </div>
            <div className="text-muted text-sm">Approved</div>
          </div>
          <div className="card" style={{ flex: 1, minWidth: 140 }}>
            <div style={{ fontSize: 28, fontWeight: 800, color: "#f85149" }}>
              {stats.by_verdict?.request_changes || 0}
            </div>
            <div className="text-muted text-sm">Changes Requested</div>
          </div>
        </div>
      )}

      {/* Filter Tabs */}
      <div className="flex gap-8" style={{ marginBottom: 16 }}>
        {["all", "pr_review", "commit_review", "issue_review"].map(f => (
          <button
            key={f}
            className={`btn ${filter === f ? "btn-primary" : "btn-secondary"}`}
            style={{ padding: "4px 12px", fontSize: 13 }}
            onClick={() => setFilter(f)}
          >
            {f === "all" ? "All" : TYPE_LABELS[f]?.label}
          </button>
        ))}
      </div>

      {/* Reviews Table */}
      {filtered.length === 0 ? (
        <div className="card" style={{ textAlign: "center", padding: 48 }}>
          <p className="text-muted">No reviews yet — run a review to see it here.</p>
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: "hidden" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border)" }}>
                {["Type", "Repo", "Title", "Verdict", "Score", "Date"].map(h => (
                  <th key={h} style={{
                    padding: "10px 16px", textAlign: "left",
                    fontSize: 12, color: "var(--text-muted)", fontWeight: 600,
                  }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((r, i) => {
                const type = TYPE_LABELS[r.type] || { label: r.type, color: "badge-blue" };
                const verdict = VERDICT_LABELS[r.verdict];
                return (
                  <tr key={r.id} style={{
                    borderBottom: i < filtered.length - 1 ? "1px solid var(--border)" : "none",
                  }}>
                    <td style={{ padding: "10px 16px" }}>
                      <span className={`badge ${type.color}`}>{type.label}</span>
                    </td>
                    <td style={{ padding: "10px 16px" }}>
                      <code style={{ fontSize: 12 }}>{r.repo}</code>
                    </td>
                    <td style={{ padding: "10px 16px", fontSize: 13, maxWidth: 300 }}>
                      <div style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {r.title || `#${r.reference}`}
                      </div>
                    </td>
                    <td style={{ padding: "10px 16px" }}>
                      {verdict
                        ? <span className={`badge ${verdict.color}`}>{verdict.label}</span>
                        : <span className="text-muted text-sm">—</span>
                      }
                    </td>
                    <td style={{ padding: "10px 16px", fontWeight: 700 }}>
                      {r.score ? `${r.score}/10` : "—"}
                    </td>
                    <td style={{ padding: "10px 16px" }}>
                      <span className="text-muted text-sm">
                        {new Date(r.created_at).toLocaleDateString()}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}