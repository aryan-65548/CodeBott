export default function CommitReviewCard({ data }) {
  if (!data) return null;

  const qualityConfig = {
    good:       { className: "badge-green",  label: "Good" },
    acceptable: { className: "badge-yellow", label: "Acceptable" },
    poor:       { className: "badge-red",    label: "Poor" },
  };

  const severityConfig = {
    critical:   { className: "badge-red" },
    warning:    { className: "badge-yellow" },
    suggestion: { className: "badge-blue" },
  };

  const quality = qualityConfig[data.commit_message_quality] || qualityConfig.acceptable;

  return (
    <div className="card" style={{ marginTop: 24 }}>

      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <div className="flex items-center gap-8">
            <code style={{ fontSize: 13, color: "var(--blue)" }}>
              {data.sha}
            </code>
            <span className={`badge ${quality.className}`}>
              Message: {quality.label}
            </span>
          </div>
          <p className="text-muted mt-8">{data.summary}</p>
        </div>
        <div style={{ textAlign: "right", flexShrink: 0, marginLeft: 16 }}>
          <div style={{ fontSize: 28, fontWeight: 800 }}>
            {data.score}
            <span className="text-muted" style={{ fontSize: 14 }}>/10</span>
          </div>
        </div>
      </div>

      {/* Commit Message Feedback */}
      {data.commit_message_feedback && (
        <div style={{
          marginTop: 16,
          padding: "10px 14px",
          background: "var(--bg-secondary)",
          borderRadius: 6,
          borderLeft: "3px solid var(--blue)",
        }}>
          <p className="text-sm text-muted">
             {data.commit_message_feedback}
          </p>
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
                  <p style={{ fontWeight: 600, marginTop: 8, fontSize: 14 }}>
                    {issue.title}
                  </p>
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
              <li key={i} className="text-sm"
                style={{ color: "#3fb950", marginTop: 6 }}>
                {p}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}