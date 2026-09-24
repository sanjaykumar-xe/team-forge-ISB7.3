import React, { useState, useEffect } from "react";

export default function UserReportsModal({ token, user, apiUrl, isOpen, onClose, onSelectReport }) {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [emailStatus, setEmailStatus] = useState({});

  useEffect(() => {
    if (!isOpen || !token) return;
    setLoading(true);

    fetch(`${apiUrl || "http://127.0.0.1:8000"}/api/user/jobs`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((data) => {
        setJobs(data.jobs || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load user jobs:", err);
        setLoading(false);
      });
  }, [isOpen, token, apiUrl]);

  const handleSendEmail = async (jobId) => {
    setEmailStatus((prev) => ({
      ...prev,
      [jobId]: { sending: true, message: "Dispatching email...", success: null },
    }));

    try {
      const headers = { "Content-Type": "application/json" };
      if (token) headers["Authorization"] = `Bearer ${token}`;

      const res = await fetch(`${apiUrl || "http://127.0.0.1:8000"}/api/jobs/${jobId}/send-email`, {
        method: "POST",
        headers,
        body: JSON.stringify({ email: user?.email }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to dispatch email");

      setEmailStatus((prev) => ({
        ...prev,
        [jobId]: { sending: false, message: `Dispatched to ${data.email || "your Gmail"}!`, success: true },
      }));
    } catch (err) {
      setEmailStatus((prev) => ({
        ...prev,
        [jobId]: { sending: false, message: err.message || "Failed to send", success: false },
      }));
    }
  };

  if (!isOpen) return null;

  return (
    <div className="auth-modal-backdrop" onClick={onClose}>
      <div className="reports-modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="reports-modal-header">
          <div>
            <h3 className="reports-modal-title">My Validated Reports</h3>
            <p className="reports-modal-subtitle">Saved dossiers and validation history</p>
          </div>
          <button type="button" className="reports-close-btn" onClick={onClose} aria-label="Close modal">
            &times;
          </button>
        </div>

        <div className="reports-list-container">
          {loading ? (
            <div className="reports-loading-state">Loading your reports...</div>
          ) : jobs.length === 0 ? (
            <div className="reports-empty-state">
              <span className="reports-empty-icon">&#128194;</span>
              <p>No validation reports yet.</p>
              <span className="reports-empty-hint">Submit an idea on the dashboard to build your dossier library.</span>
            </div>
          ) : (
            jobs.map((job) => {
              const res = job.result;
              const extracted = res?.extracted_data || {};
              const title = extracted.product_name || "Startup Pitch";
              const industry = extracted.industry || "General";
              const dateStr = job.created_at ? new Date(job.created_at).toLocaleDateString() : "";
              const st = emailStatus[job.job_id];

              return (
                <div key={job.job_id} className="report-item-card">
                  <div className="report-item-info">
                    <div className="report-item-header">
                      <span className="report-item-title">{title}</span>
                      <span className={`report-status-badge status-${job.status}`}>
                        {job.status}
                      </span>
                    </div>
                    <div className="report-item-pitch">{job.idea_text}</div>
                    <div className="report-item-meta">
                      <span>&#128188; {industry}</span>
                      {dateStr && <span>&#128197; {dateStr}</span>}
                      {job.email && <span>&#9993; {job.email}</span>}
                    </div>

                    {st && (
                      <div
                        style={{
                          marginTop: "8px",
                          fontSize: "12px",
                          fontWeight: 600,
                          color: st.success ? "#16a34a" : "#dc2626",
                        }}
                      >
                        {st.success ? "&#10003; " : "&#9888; "}
                        {st.message}
                      </div>
                    )}
                  </div>
                  <div className="report-item-actions" style={{ display: "flex", flexDirection: "column", gap: "8px", alignItems: "flex-end" }}>
                    {job.result ? (
                      <>
                        <button
                          type="button"
                          className="report-open-btn"
                          onClick={() => {
                            onSelectReport(job.result);
                            onClose();
                          }}
                        >
                          Open Dossier &rarr;
                        </button>

                        <button
                          type="button"
                          className="report-email-action-btn"
                          style={{
                            background: "#f8fafc",
                            color: "#334155",
                            border: "1px solid #cbd5e1",
                            padding: "6px 12px",
                            borderRadius: "6px",
                            fontSize: "12px",
                            fontWeight: 600,
                            cursor: "pointer",
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "5px",
                          }}
                          onClick={() => handleSendEmail(job.job_id)}
                          disabled={st?.sending}
                        >
                          &#9993; {st?.sending ? "Sending..." : "Email Me"}
                        </button>
                      </>
                    ) : (
                      <span className="report-processing-text">Validating...</span>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
