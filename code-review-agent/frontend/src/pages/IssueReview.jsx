import { useState } from "react";
import { reviewIssue } from "../api/client";
import IssuePanel from "../components/IssuePanel";

export default function IssueReview() {
  const [repo, setRepo] = useState("tiangolo/fastapi");
  const [issueNumber, setIssueNumber] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleReview = async () => {
    if (!repo || !issueNumber) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await reviewIssue(repo, parseInt(issueNumber));
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 800, marginBottom: 8 }}>Issue Analysis</h1>
      <p className="text-muted" style={{ marginBottom: 24 }}>
        Enter a repo and issue number to get an AI analysis.
      </p>

      <div className="card">
        <div className="flex gap-16" style={{ flexWrap: "wrap" }}>
          <div style={{ flex: 2, minWidth: 200 }}>
            <label className="text-sm text-muted">Repository</label>
            <input className="input mt-8" placeholder="owner/repo"
              value={repo} onChange={e => setRepo(e.target.value)} />
          </div>
          <div style={{ flex: 1, minWidth: 120 }}>
            <label className="text-sm text-muted">Issue Number</label>
            <input className="input mt-8" placeholder="e.g. 1234"
              type="number" value={issueNumber}
              onChange={e => setIssueNumber(e.target.value)} />
          </div>
          <div style={{ display: "flex", alignItems: "flex-end" }}>
            <button className="btn btn-primary"
              onClick={handleReview}
              disabled={loading || !repo || !issueNumber}>
              {loading ? <><div className="spinner" />Analyzing...</> : "Analyze Issue"}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div style={{
          marginTop: 16, padding: "12px 16px",
          background: "rgba(248,81,73,0.1)",
          border: "1px solid rgba(248,81,73,0.3)",
          borderRadius: 8, color: "#f85149", fontSize: 14,
        }}>✗ {error}</div>
      )}

      {loading && (
        <div className="card" style={{ marginTop: 24, textAlign: "center", padding: 48 }}>
          <div className="spinner" style={{ margin: "0 auto 16px", width: 32, height: 32 }} />
          <p className="text-muted">Analyzing issue...</p>
        </div>
      )}

      {result && <IssuePanel data={result} />}
    </div>
  );
}