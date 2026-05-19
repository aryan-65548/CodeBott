export default function ReviewCard({ data }) {
  if (!data) return null;

  const verdictConfig = {
    approve: { label: "Approve", className: "badge-green", icon: "✓" },
    request_changes: { label: "Request Changes", className: "badge-red", icon: "✗" },
    needs_discussion: { label: "Needs Discussion", className: "badge-yellow", icon: "◎" },
  };

  const severityConfig = {
    critical: { className: "badge-red", icon: "🔴" },
    warning: { className: "badge-yellow", icon: "🟡" },
    suggestion: { className: "badge-blue", icon: "🔵" },
  };

  const verdict = verdictConfig[data.verdict] || verdictConfig.needs_discussion;

  return (
    <div className="card" style={{ marginTop: 24 }}>

      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 style={{ fontSize: 18, fontWeight: 700 }}>
            PR #{data.pr_number} — {data.pr_title}
          </h2>
          <p className="text-muted mt-8">{data.summary}</p>
        </div>
        <div style={{ textAlign: "right", flexShrink: 0, marginLeft: 16 }}>
          <span className={`badge ${verdict.className}`}>
            {verdict.icon} {verdict.label}
          </span>
          <div style={{ fontSize: 28, fontWeight: 800, marginTop: 8 }}>
            {data.score}
            <span className="text-muted" style={{ fontSize: 14 }}>/10</span>
          </div>
        </div>
      </div>

      {/* Security Flags */}
      {data.security_flags?.length > 0 && (
        <div style={{
          marginTop: 16,
          padding: "10px 14px",
          background: "rgba(248,81,73,0.1)",
          border: "1px solid rgba(248,81,73,0.3)",
          borderRadius: 6,
        }}>
          <strong style={{ color: "#f85149", fontSize: 13 }}> Security Flags</strong>
          <ul style={{ marginTop: 6, paddingLeft: 16 }}>
            {data.security_flags.map((flag, i) => (
              <li key={i} className="text-sm" style={{ color: "#f85149", marginTop: 4 }}>{flag}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Issues */}
      {data.issues?.length > 0 && (
        <div style={{ marginTop: 20 }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 10 }}>
            Issues ({data.issues.length})
          </h3>
          <div className="flex flex-col gap-8">
            {data.issues.map((issue, i) => {
              const sev = severityConfig[issue.severity] || severityConfig.suggestion;
              return (
                <div key={i} style={{
                  background: "var(--bg-secondary)",
                  border: "1px solid var(--border)",
                  borderRadius: 6,
                  padding: "12px 14px",
                }}>
                  <div className="flex items-center gap-8">
                    <span className={`badge ${sev.className}`}>{issue.severity}</span>
                    {issue.file && (
                      <code style={{ fontSize: 12, color: "var(--text-muted)" }}>
                        {issue.file}
                      </code>
                    )}
                  </div>
                  <p style={{ fontWeight: 600, marginTop: 8, fontSize: 14 }}>{issue.title}</p>
                  <p className="text-muted mt-8">{issue.description}</p>
                  {issue.suggestion && (
                    <div style={{
                      marginTop: 8,
                      padding: "8px 12px",
                      background: "rgba(56,139,253,0.08)",
                      borderRadius: 4,
                      borderLeft: "3px solid var(--blue)",
                    }}>
                      <p className="text-sm" style={{ color: "var(--blue)" }}>
                         {issue.suggestion}
                      </p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Positives */}
      {data.positives?.length > 0 && (
        <div style={{ marginTop: 20 }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 10 }}>
            What's Good
          </h3>
          <ul style={{ paddingLeft: 16 }}>
            {data.positives.map((p, i) => (
              <li key={i} className="text-sm" style={{ color: "#3fb950", marginTop: 6 }}>{p}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Footer */}
      <div className="flex gap-16 mt-24" style={{ borderTop: "1px solid var(--border)", paddingTop: 16 }}>
        {data.estimated_review_time && (
          <span className="text-muted"> {data.estimated_review_time}</span>
        )}
        {data.budget_summary && (
          <span className="text-muted">
             {data.budget_summary.included}/{data.budget_summary.total_files} files reviewed
          </span>
        )}
      </div>
    </div>
  );
}