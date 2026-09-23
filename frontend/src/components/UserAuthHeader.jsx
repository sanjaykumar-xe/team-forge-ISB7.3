import React, { useState } from "react";

export default function UserAuthHeader({ user, token, onLogin, onLogout, onOpenReports }) {
  const [showDevLogin, setShowDevLogin] = useState(false);
  const [devEmail, setDevEmail] = useState("");

  const handleDevSubmit = (e) => {
    e.preventDefault();
    if (!devEmail || !devEmail.includes("@")) return;
    onLogin(`dev_${devEmail.trim()}`);
    setShowDevLogin(false);
  };

  return (
    <div className="user-auth-header-container">
      {user ? (
        <div className="user-logged-in-badge">
          {user.avatar_url ? (
            <img src={user.avatar_url} alt={user.name || "User"} className="user-avatar-img" />
          ) : (
            <div className="user-avatar-fallback">
              {(user.name || user.email || "U")[0].toUpperCase()}
            </div>
          )}
          <div className="user-info-text">
            <span className="user-display-name">{user.name || "Founder"}</span>
            <span className="user-display-email">{user.email}</span>
          </div>
          <button type="button" className="auth-action-btn reports-btn" onClick={onOpenReports}>
            📁 My Reports
          </button>
          <button type="button" className="auth-action-btn logout-btn" onClick={onLogout}>
            Sign Out
          </button>
        </div>
      ) : (
        <div className="user-logged-out-actions">
          <button
            type="button"
            className="google-signin-btn"
            onClick={() => setShowDevLogin(true)}
          >
            <svg className="google-icon" viewBox="0 0 24 24" width="18" height="18">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
              />
            </svg>
            <span>Sign in with Google</span>
          </button>
        </div>
      )}

      {/* Dev / Google OAuth Modal */}
      {showDevLogin && (
        <div className="auth-modal-backdrop" onClick={() => setShowDevLogin(false)}>
          <div className="auth-modal-card" onClick={(e) => e.stopPropagation()}>
            <h3 className="auth-modal-title">Sign in to Team Forge</h3>
            <p className="auth-modal-desc">
              Connect your Gmail to enable background research delivery and access your saved reports history.
            </p>

            <form onSubmit={handleDevSubmit} className="auth-modal-form">
              <label className="auth-label">Gmail / Email Address:</label>
              <input
                type="email"
                className="auth-input"
                placeholder="founder@gmail.com"
                value={devEmail}
                onChange={(e) => setDevEmail(e.target.value)}
                autoFocus
                required
              />
              <div className="auth-modal-buttons">
                <button type="submit" className="auth-submit-btn">
                  Continue &rarr;
                </button>
                <button
                  type="button"
                  className="auth-cancel-btn"
                  onClick={() => setShowDevLogin(false)}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
