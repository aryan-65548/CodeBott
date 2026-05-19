import { useState } from "react";
import { reviewPR } from "../api/client";
import ReviewCard from "../components/ReviewCard";
import DiffViewer from "../components/DiffViewer";

export default function PRReview() {
  const [repo, setRepo] = useState("tiangolo/fastapi");
  const [prNumber, setPrNumber] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [prData, setPrData] = useState(null);
  const [error, setError] = useState(null);

  const handleReview = async () => {
    if (!repo || !prNumber) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setPrData(null);

    try {
      // fetch PR diff for DiffViewer
      const diffRes = await fetch(
        `http://localhost:8000/api/pr-files?repo=${repo}&pr_number=${prNumber}`
      ).then(r => r.json()).catch(() => null);
      setPrData(diffRes);

      const res = await reviewPR(repo, parseInt(prNumber));
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 800, marginBottom: 8 }}>PR Review</h1>
      <p className="text-muted" style={{ marginBottom: 24 }}>
        Enter a GitHub repo and PR number to get an AI review.
      </p>

      <div className="card">
        <div className="flex gap-16" style={{ flexWrap: "wrap" }}>
          <div style={{ flex: 2, minWidth: 200 }}>
            <label className="text-sm text-muted">Repository</label>
            <input
              className="input mt-8"
              placeholder="owner/repo"
              value={repo}
              onChange={e => setRepo(e.target.value)}
            />
          </div>
          <div style={{ flex: 1, minWidth: 120 }}>
            <label className="text-sm text-muted">PR Number</label>
            <input
              className="input mt-8"
              placeholder="e.g. 1234"
              type="number"
              value={prNumber}
              onChange={e => setPrNumber(e.target.value)}
            />
          </div>
          <div style={{ display: "flex", alignItems: "flex-end" }}>
            <button
              className="btn btn-primary"
              onClick={handleReview}
              disabled={loading || !repo || !prNumber}
            >
              {loading ? (
                <><div className="spinner" />Reviewing...</>
              ) : "Review PR"}
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
        }}>
          ✗ {error}
        </div>
      )}

      {loading && (
        <div className="card" style={{ marginTop: 24, textAlign: "center", padding: 48 }}>
          <div className="spinner" style={{ margin: "0 auto 16px", width: 32, height: 32 }} />
          <p className="text-muted">Fetching PR and running AI review...</p>
          <p className="text-muted text-sm mt-8">This takes 5-15 seconds</p>
        </div>
      )}

      {result && <ReviewCard data={result} />}
      {result && prData?.files && <DiffViewer files={prData.files} />}
    </div>
  );
}