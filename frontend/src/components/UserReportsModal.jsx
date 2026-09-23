import React, { useState, useEffect } from "react";

export default function UserReportsModal({ token, apiUrl, isOpen, onClose, onSelectReport }) {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

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

  if (!isOpen) return null;

  return (
    <div className="auth-modal-backdrop" onClick={onClose}>
      <div className="reports-modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="reports-modal-header">
          <div>
            <h3 className="reports-modal-title">My Validated Reports</h3>
            <p className="reports-modal-subtitle">Saved dossiers and validation history</p>
          </div>
          <button type="button" className="reports-close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="reports-list-container">
          {loading ? (
            <div className="reports-loading-state">Loading your reports...</div>
          ) : jobs.length === 0 ? (
            <div className="reports-empty-state">
              <span className="reports-empty-icon">📁</span>
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
                      <span>🏷️ {industry}</span>
                      {dateStr && <span>📅 {dateStr}</span>}
                    </div>
                  </div>
                  <div className="report-item-actions">
                    {job.result ? (
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
