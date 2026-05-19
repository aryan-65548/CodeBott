export default function IssuePanel({ data }) {
  if (!data) return null;

  const priorityConfig = {
    critical: { className: "badge-red",    icon: "🔴" },
    high:     { className: "badge-red",    icon: "🟠" },
    medium:   { className: "badge-yellow", icon: "🟡" },
    low:      { className: "badge-blue",   icon: "🔵" },
  };

  const categoryConfig = {
    bug:             { label: "Bug" },
    feature_request: { label: "Feature Request" },
    question:        { label: "Question" },
    documentation:   { label: "Documentation" },
    performance:     { label: "Performance" },
    security:        { label: "Security" },
  };

  const priority = priorityConfig[data.priority] || priorityConfig.medium;
  const category = categoryConfig[data.category] || {label: data.category };

  return (
    <div className="card" style={{ marginTop: 24 }}>

      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <div className="flex items-center gap-8">
            <span>Issue #{data.issue_number}</span>
            <span className={`badge ${priority.className}`}>
              {priority.icon} {data.priority} priority
            </span>
            <span className="badge badge-purple">
              {category.icon} {category.label}
            </span>
          </div>
          <p className="text-muted mt-8">{data.summary}</p>
        </div>
        <div style={{ textAlign: "right", flexShrink: 0, marginLeft: 16 }}>
          <div style={{ fontSize: 13, color: "var(--text-muted)" }}>Clarity</div>
          <div style={{ fontSize: 28, fontWeight: 800 }}>
            {data.clarity_score}
            <span className="text-muted" style={{ fontSize: 14 }}>/10</span>
          </div>
        </div>
      </div>

      {/* Reproducible */}
      <div style={{ marginTop: 16 }}>
        <span className={`badge ${data.is_reproducible ? "badge-green" : "badge-red"}`}>
          {data.is_reproducible ? "✓ Reproducible" : "✗ Not reproducible"}
        </span>
      </div>

      {/* Missing Info */}
      {data.missing_info?.length > 0 && (
        <div style={{
          marginTop: 16,
          padding: "10px 14px",
          background: "rgba(210,153,34,0.08)",
          border: "1px solid rgba(210,153,34,0.3)",
          borderRadius: 6,
        }}>
          <strong style={{ fontSize: 13, color: "var(--yellow)" }}>
            ⚠ Missing Information
          </strong>
          <ul style={{ paddingLeft: 16, marginTop: 6 }}>
            {data.missing_info.map((info, i) => (
              <li key={i} className="text-sm"
                style={{ color: "var(--yellow)", marginTop: 4 }}>
                {info}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Suggested Labels */}
      {data.suggested_labels?.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <p className="text-sm text-muted" style={{ marginBottom: 8 }}>
            Suggested Labels
          </p>
          <div className="flex gap-8" style={{ flexWrap: "wrap" }}>
            {data.suggested_labels.map((label, i) => (
              <span key={i} className="badge badge-purple">{label}</span>
            ))}
          </div>
        </div>
      )}

      {/* Suggested Approach */}
      {data.suggested_approach && (
        <div style={{
          marginTop: 16,
          padding: "10px 14px",
          background: "rgba(56,139,253,0.08)",
          borderRadius: 6,
          borderLeft: "3px solid var(--blue)",
        }}>
          <strong style={{ fontSize: 13, color: "var(--blue)" }}>
             Suggested Approach
          </strong>
          <p className="text-sm mt-8">{data.suggested_approach}</p>
        </div>
      )}
    </div>
  );
}