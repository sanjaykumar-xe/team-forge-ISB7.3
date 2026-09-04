import React from "react";

/**
 * CustomerSegments Component
 * Renders multidimensional customer persona cards with distinct End User vs Decision Maker roles,
 * acute pain points, buying behaviors, and domain terminology.
 */
export default function CustomerSegments({ segments = [] }) {
  if (!segments || segments.length === 0) return null;

  return (
    <div className="customer-segments-section">
      <div className="section-masthead">
        <div className="section-eyebrow-row">
          <span className="section-badge badge-blue">§ TARGET CUSTOMER SEGMENTATION</span>
          <span className="section-count">{segments.length} Segments Identified</span>
        </div>
        <h3 className="section-headline">Granular Persona Breakdown & Buying Behavior</h3>
      </div>

      <div className="segments-grid">
        {segments.map((seg, idx) => (
          <div key={idx} className="segment-card">
            <div className="segment-card-header">
              <span className="segment-index-tag">SEGMENT 0{idx + 1}</span>
              <h4 className="segment-title">{seg.segment_name}</h4>
              <p className="segment-who">{seg.who_they_are}</p>
            </div>

            {/* End Users vs Decision Makers */}
            <div className="segment-roles-bar">
              <div className="role-col">
                <span className="role-label">END USERS</span>
                <span className="role-value">{seg.end_users}</span>
              </div>
              <div className="role-col">
                <span className="role-label">DECISION MAKERS</span>
                <span className="role-value">{seg.decision_makers}</span>
              </div>
            </div>

            {/* Pain Points */}
            {Array.isArray(seg.pain_points) && seg.pain_points.length > 0 && (
              <div className="segment-block">
                <span className="segment-subhead pain-subhead">ACUTE PAIN POINTS</span>
                <ul className="segment-bullet-list pain-list">
                  {seg.pain_points.map((pain, i) => (
                    <li key={i}>{pain}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Primary Needs & Motivations */}
            {Array.isArray(seg.primary_needs) && seg.primary_needs.length > 0 && (
              <div className="segment-block">
                <span className="segment-subhead">CORE REQUIREMENTS</span>
                <ul className="segment-bullet-list">
                  {seg.primary_needs.map((need, i) => (
                    <li key={i}>{need}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Buying Behavior */}
            {seg.buying_behavior && (
              <div className="segment-block buying-block">
                <span className="segment-subhead">BUYING BEHAVIOR & ADOPTION</span>
                <p className="segment-buying-text">{seg.buying_behavior}</p>
              </div>
            )}

            {/* Terminology Tags */}
            {Array.isArray(seg.industry_terminology) && seg.industry_terminology.length > 0 && (
              <div className="segment-terms-row">
                <span className="terms-label">DOMAIN JARGON:</span>
                <div className="terms-chip-container">
                  {seg.industry_terminology.map((term, i) => (
                    <span key={i} className="term-chip">
                      #{term}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
