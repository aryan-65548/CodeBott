import { useState } from "react";

export default function DiffViewer({ files }) {
  const [expanded, setExpanded] = useState({});

  if (!files || files.length === 0) return null;

  const toggle = (filename) =>
    setExpanded((prev) => ({ ...prev, [filename]: !prev[filename] }));

  const getLineStyle = (line) => {
    if (line.startsWith("+"))
      return { background: "rgba(46,160,67,0.15)", color: "#3fb950" };
    if (line.startsWith("-"))
      return { background: "rgba(248,81,73,0.15)", color: "#f85149" };
    return { color: "var(--text-muted)" };
  };

  const statusBadge = (status) => {
    const map = {
      added:    { label: "added",    className: "badge-green" },
      modified: { label: "modified", className: "badge-blue" },
      removed:  { label: "removed",  className: "badge-red" },
    };
    const s = map[status] || map.modified;
    return <span className={`badge ${s.className}`}>{s.label}</span>;
  };

  return (
    <div style={{ marginTop: 24 }}>
      <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12 }}>
        Changed Files ({files.length})
      </h3>

      <div className="flex flex-col gap-8">
        {files.map((file, i) => (
          <div
            key={i}
            style={{
              border: "1px solid var(--border)",
              borderRadius: 6,
              overflow: "hidden",
            }}
          >
            {/* File Header */}
            <div
              className="flex items-center justify-between"
              style={{
                padding: "8px 14px",
                background: "var(--bg-secondary)",
                cursor: "pointer",
                userSelect: "none",
              }}
              onClick={() => toggle(file.filename)}
            >
              <div className="flex items-center gap-8">
                <span style={{ color: "var(--text-muted)", fontSize: 12 }}>
                  {expanded[file.filename] ? "▾" : "▸"}
                </span>
                {statusBadge(file.status)}
                <code style={{ fontSize: 13 }}>{file.filename}</code>
              </div>
              <div className="flex gap-8">
                <span style={{ fontSize: 12, color: "#3fb950" }}>
                  +{file.additions}
                </span>
                <span style={{ fontSize: 12, color: "#f85149" }}>
                  -{file.deletions}
                </span>
              </div>
            </div>

            {/* Diff Content */}
            {expanded[file.filename] && file.patch && (
              <div
                style={{
                  overflowX: "auto",
                  background: "var(--bg)",
                }}
              >
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
                  <tbody>
                    {file.patch.split("\n").map((line, j) => (
                      <tr key={j} style={getLineStyle(line)}>
                        <td
                          style={{
                            padding: "1px 12px",
                            whiteSpace: "pre",
                            fontFamily: "monospace",
                            width: "100%",
                          }}
                        >
                          {line || " "}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {expanded[file.filename] && !file.patch && (
              <div style={{ padding: "12px 14px" }}>
                <p className="text-muted text-sm">No patch available for this file.</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}