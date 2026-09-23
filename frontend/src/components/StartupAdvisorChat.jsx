import React, { useState, useEffect, useRef } from "react";

const SECTION_LABELS = {
  "section-overview": "Executive Overview",
  "section-context": "Extracted Pitch & Problem",
  "section-whitespace": "White-Space Map",
  "section-market": "Market Sizing (TAM/SAM)",
  "section-personas": "Customer Personas",
  "section-competitors": "Competitor Matrix",
  "section-swot": "SWOT & Risk Matrix",
  "section-mvp": "MVP Product Scope",
  "section-gtm": "Go-To-Market Strategy",
  "section-sources": "Verified Citations",
};

export default function StartupAdvisorChat({ ideaId, currentView, apiUrl }) {
  const [messages, setMessages] = useState([
    {
      role: "advisor",
      content:
        "Welcome! I am your Conversational Startup Advisor. Ask me any follow-up question regarding the market sizing, competitor positioning, MVP roadmap, or strategic risks discovered for this idea.",
      grounded_in: ["validation_dossier"],
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(true);
  const messagesEndRef = useRef(null);

  const activeViewLabel = SECTION_LABELS[currentView] || currentView || "General Overview";

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async (textToSend) => {
    const query = textToSend || input;
    if (!query.trim() || loading) return;

    const userMessage = { role: "user", content: query.trim() };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput("");
    setLoading(true);

    try {
      const endpoint = `${apiUrl || "http://127.0.0.1:8000"}/api/advisor/chat`;
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          idea_id: ideaId,
          message: query.trim(),
          current_view: currentView,
          conversation_history: updatedMessages.map((m) => ({
            role: m.role,
            content: m.content,
          })),
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }

      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        {
          role: "advisor",
          content: data.reply,
          grounded_in: data.grounded_in || [],
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "advisor",
          content: `Unable to retrieve advisor response: ${err.message}. Please verify the backend connection.`,
          grounded_in: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <section id="section-advisor" className="advisor-chat-section">
      <div className="advisor-chat-card">
        {/* Header */}
        <div className="advisor-chat-header">
          <div className="advisor-header-title-row">
            <div className="advisor-badge-pill">
              <span className="advisor-live-dot" />
              <span>CONVERSATIONAL ADVISOR</span>
            </div>
            <h3 className="advisor-header-heading">Interactive Venture Partner</h3>
          </div>
          <div className="advisor-header-meta">
            <span className="advisor-context-tag">
              Viewing: <strong>{activeViewLabel}</strong>
            </span>
            <button
              type="button"
              className="advisor-toggle-btn"
              onClick={() => setIsOpen(!isOpen)}
              aria-label="Toggle chat visibility"
            >
              {isOpen ? "Collapse ▲" : "Expand ▼"}
            </button>
          </div>
        </div>

        {isOpen && (
          <>
            {/* Context Notice */}
            <div className="advisor-grounding-banner">
              <span className="advisor-banner-icon">🛡️</span>
              <span className="advisor-banner-text">
                <strong>Anti-Hallucination Grounding:</strong> Advisor answers are strictly bound to the empirical data collected for this startup idea.
              </span>
            </div>

            {/* Message Thread */}
            <div className="advisor-messages-container">
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`advisor-msg-row ${
                    msg.role === "user" ? "advisor-msg-user" : "advisor-msg-bot"
                  }`}
                >
                  <div className="advisor-msg-bubble">
                    <div className="advisor-msg-sender">
                      {msg.role === "user" ? "You" : "Advisor"}
                    </div>
                    <div className="advisor-msg-text">{msg.content}</div>

                    {msg.role === "advisor" && (
                      <div className="advisor-grounding-tags">
                        {msg.grounded_in && msg.grounded_in.length > 0 ? (
                          <>
                            <span className="grounded-label">Grounded in:</span>
                            {msg.grounded_in.map((sec, sIdx) => (
                              <span key={sIdx} className="grounded-pill">
                                {sec.replace(/_/g, " ")}
                              </span>
                            ))}
                          </>
                        ) : (
                          <span className="grounded-pill ungrounded-pill">
                            Direct Inquiry / Uncovered
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="advisor-msg-row advisor-msg-bot">
                  <div className="advisor-msg-bubble advisor-loading-bubble">
                    <span className="advisor-spinner" />
                    <span>Analyzing validated context bundle...</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Quick Suggestions based on active section */}
            <div className="advisor-suggestions-row">
              <span className="suggestions-label">Suggestions:</span>
              <button
                type="button"
                className="suggestion-chip"
                onClick={() => handleSend("Tell me more about this section and key findings")}
              >
                "Tell me more about this"
              </button>
              <button
                type="button"
                className="suggestion-chip"
                onClick={() => handleSend("What is the biggest operational or market risk?")}
              >
                "What is the biggest risk?"
              </button>
              <button
                type="button"
                className="suggestion-chip"
                onClick={() => handleSend("What are the most promising market gaps to exploit?")}
              >
                "Where is the white space?"
              </button>
            </div>

            {/* Input Bar */}
            <div className="advisor-input-bar">
              <textarea
                className="advisor-textarea"
                rows="2"
                placeholder={`Ask a question relative to ${activeViewLabel} or general strategy...`}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={loading}
              />
              <button
                type="button"
                className="advisor-send-button"
                onClick={() => handleSend()}
                disabled={loading || !input.trim()}
              >
                {loading ? "Thinking..." : "Ask Advisor →"}
              </button>
            </div>
          </>
        )}
      </div>
    </section>
  );
}
