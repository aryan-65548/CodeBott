import { useState } from "react";
import { reviewCommit } from "../api/client";
import CommitReviewCard from "../components/CommitReviewCard";

export default function CommitReview() {
  const [repo, setRepo] = useState("tiangolo/fastapi");
  const [sha, setSha] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleReview = async () => {
    if (!repo || !sha) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await reviewCommit(repo, sha);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 800, marginBottom: 8 }}>Commit Review</h1>
      <p className="text-muted" style={{ marginBottom: 24 }}>
        Enter a repo and commit SHA to get an AI review.
      </p>

      <div className="card">
        <div className="flex gap-16" style={{ flexWrap: "wrap" }}>
          <div style={{ flex: 2, minWidth: 200 }}>
            <label className="text-sm text-muted">Repository</label>
            <input className="input mt-8" placeholder="owner/repo"
              value={repo} onChange={e => setRepo(e.target.value)} />
          </div>
          <div style={{ flex: 1, minWidth: 160 }}>
            <label className="text-sm text-muted">Commit SHA</label>
            <input className="input mt-8" placeholder="e.g. a3f8c2d"
              value={sha} onChange={e => setSha(e.target.value)} />
          </div>
          <div style={{ display: "flex", alignItems: "flex-end" }}>
            <button className="btn btn-primary"
              onClick={handleReview}
              disabled={loading || !repo || !sha}>
              {loading ? <><div className="spinner" />Reviewing...</> : "Review Commit"}
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
          <p className="text-muted">Reviewing commit...</p>
        </div>
      )}

      {result && <CommitReviewCard data={result} />}
    </div>
  );
}