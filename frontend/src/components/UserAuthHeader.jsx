import React, { useState } from "react";
import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || "";

export default function UserAuthHeader({ user, token, onLogin, onLogout, onOpenReports }) {
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [emailInput, setEmailInput] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    if (!emailInput || !emailInput.includes("@")) {
      setErrorMessage("Please enter a valid Gmail address.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage("");

    try {
      await onLogin(`dev_${emailInput.trim()}`);
      setShowAuthModal(false);
      setEmailInput("");
    } catch (err) {
      setErrorMessage(err.message || "Failed to sign in. Please verify backend connection.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleGoogleSuccess = async (credentialResponse) => {
    if (!credentialResponse?.credential) return;
    setIsSubmitting(true);
    setErrorMessage("");

    try {
      await onLogin(credentialResponse.credential);
      setShowAuthModal(false);
    } catch (err) {
      setErrorMessage(err.message || "Google authentication failed.");
    } finally {
      setIsSubmitting(false);
    }
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
            onClick={() => {
              setErrorMessage("");
              setShowAuthModal(true);
            }}
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

      {/* Auth Modal */}
      {showAuthModal && (
        <div className="auth-modal-backdrop" onClick={() => !isSubmitting && setShowAuthModal(false)}>
          <div className="auth-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="auth-modal-top">
              <div className="auth-icon-circle">
                <svg viewBox="0 0 24 24" width="22" height="22">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
                </svg>
              </div>
              <h3 className="auth-modal-title">Sign in to Team Forge</h3>
              <p className="auth-modal-desc">
                Connect your account to access your saved dossiers and receive background validation reports in your Gmail.
              </p>
            </div>

            {errorMessage && (
              <div className="auth-error-banner" role="alert">
                <span>⚠️ {errorMessage}</span>
              </div>
            )}

            {/* Official Google OAuth One-Click (if Client ID configured) */}
            {GOOGLE_CLIENT_ID ? (
              <div className="google-oauth-wrapper">
                <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
                  <GoogleLogin
                    onSuccess={handleGoogleSuccess}
                    onError={() => setErrorMessage("Google Sign-In failed or was cancelled.")}
                    useOneTap
                  />
                </GoogleOAuthProvider>
                <div className="auth-divider">
                  <span>OR CONTINUE WITH GMAIL</span>
                </div>
              </div>
            ) : null}

            {/* Direct Gmail Input Sign-In */}
            <form onSubmit={handleEmailSubmit} className="auth-modal-form">
              <label className="auth-label">Gmail / Email Address:</label>
              <input
                type="email"
                className="auth-input"
                placeholder="founder@gmail.com"
                value={emailInput}
                onChange={(e) => setEmailInput(e.target.value)}
                autoFocus
                disabled={isSubmitting}
                required
              />

              <div className="auth-modal-buttons">
                <button type="submit" className="auth-submit-btn" disabled={isSubmitting}>
                  {isSubmitting ? "Connecting..." : "Continue with Gmail →"}
                </button>
                <button
                  type="button"
                  className="auth-cancel-btn"
                  onClick={() => setShowAuthModal(false)}
                  disabled={isSubmitting}
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
