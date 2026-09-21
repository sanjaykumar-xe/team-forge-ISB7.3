import React from "react";

export default function GTMStrategy({ data }) {
  if (!data) return null;
  const {
    positioning_statement,
    target_channels = [],
    acquisition_strategy,
    pricing_approach,
    launch_phases = [],
    key_metrics = [],
    competitive_positioning,
    analysis_status,
    message,
  } = data;

  if (analysis_status === "processing_error" && !positioning_statement) {
    return (
      <div id="section-gtm" className="gtm-strategy-section">
        <div className="section-masthead">
          <div className="section-eyebrow-row">
            <span className="section-badge badge-amber">§ GO-TO-MARKET</span>
            <span className="section-meta-tag">[PROCESSING NOTICE]</span>
          </div>
          <h3 className="section-headline">Go-To-Market Strategy</h3>
          <p className="insufficient-data-text">⚠️ {message || "GTM strategy could not be completed."}</p>
        </div>
      </div>
    );
  }

  return (
    <div id="section-gtm" className="gtm-strategy-section">
      <div className="section-masthead">
        <div className="section-eyebrow-row">
          <span className="section-badge badge-amber">§ GO-TO-MARKET</span>
          <span className="section-meta-tag">[MILESTONE 3 — TRACTION BLUEPRINT]</span>
        </div>
        <h3 className="section-headline">Go-To-Market & Traction Blueprint</h3>
        <p className="section-summary-text">
          Idea-specific channel distribution, positioning, launch phases, and early acquisition mechanics grounded in customer segment behavior.
        </p>
      </div>

      {positioning_statement && (
        <div className="positioning-statement-card">
          <div className="positioning-label-row">
            <span className="positioning-badge">CORE POSITIONING STATEMENT</span>
          </div>
          <p className="positioning-text">"{positioning_statement}"</p>
        </div>
      )}

      {target_channels && target_channels.length > 0 && (
        <div className="channels-container">
          <h4 className="sub-section-title">TARGET DISTRIBUTION & ACQUISITION CHANNELS</h4>
          <div className="channels-grid">
            {target_channels.map((chan, idx) => {
              const name = typeof chan === "string" ? chan : chan.channel || "Channel";
              const rationale = typeof chan === "object" ? chan.rationale : null;
              const fit = typeof chan === "object" ? (chan.fit_score || "high").toLowerCase() : "high";
              const tactics = typeof chan === "object" && Array.isArray(chan.tactics) ? chan.tactics : [];

              return (
                <div key={idx} className="channel-card">
                  <div className="channel-card-header">
                    <span className={`fit-score-badge fit-${fit}`}>{fit.toUpperCase()} FIT</span>
                    <span className="channel-index">CHANNEL 0{idx + 1}</span>
                  </div>
                  <h5 className="channel-name">{name}</h5>
                  {rationale && <p className="channel-rationale">{rationale}</p>}
                  {tactics.length > 0 && (
                    <div className="channel-tactics">
                      <span className="tactics-label">TACTICAL ACTIONS:</span>
                      <ul className="tactics-list">
                        {tactics.map((t, ti) => (
                          <li key={ti}>{t}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div className="gtm-details-grid">
        {acquisition_strategy && (
          <div className="gtm-detail-card">
            <h4 className="secondary-title">ACQUISITION MECHANICS</h4>
            {typeof acquisition_strategy === "string" ? (
              <p className="gtm-detail-text">{acquisition_strategy}</p>
            ) : (
              <div className="gtm-subprops">
                {acquisition_strategy.primary_method && (
                  <div className="gtm-prop">
                    <span className="prop-label">PRIMARY METHOD:</span>
                    <span className="prop-val">{acquisition_strategy.primary_method}</span>
                  </div>
                )}
                {acquisition_strategy.estimated_cac && (
                  <div className="gtm-prop">
                    <span className="prop-label">ESTIMATED CAC:</span>
                    <span className="prop-val">{acquisition_strategy.estimated_cac}</span>
                  </div>
                )}
                {acquisition_strategy.rationale && (
                  <p className="gtm-detail-text">{acquisition_strategy.rationale}</p>
                )}
              </div>
            )}
          </div>
        )}

        {pricing_approach && (
          <div className="gtm-detail-card">
            <h4 className="secondary-title">PRICING & REVENUE MODEL</h4>
            {typeof pricing_approach === "string" ? (
              <p className="gtm-detail-text">{pricing_approach}</p>
            ) : (
              <div className="gtm-subprops">
                {pricing_approach.model && (
                  <div className="gtm-prop">
                    <span className="prop-label">MODEL:</span>
                    <span className="prop-val">{pricing_approach.model}</span>
                  </div>
                )}
                {pricing_approach.price_range && (
                  <div className="gtm-prop">
                    <span className="prop-label">TARGET PRICE:</span>
                    <span className="prop-val">{pricing_approach.price_range}</span>
                  </div>
                )}
                {pricing_approach.rationale && (
                  <p className="gtm-detail-text">{pricing_approach.rationale}</p>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {launch_phases && launch_phases.length > 0 && (
        <div className="launch-phases-container">
          <h4 className="sub-section-title">PHASED ROLLOUT TIMELINE</h4>
          <div className="phases-timeline">
            {launch_phases.map((ph, idx) => {
              const name = typeof ph === "string" ? ph : ph.phase || `Phase ${idx + 1}`;
              const duration = typeof ph === "object" ? ph.duration : null;
              const objs = typeof ph === "object" && Array.isArray(ph.objectives) ? ph.objectives : [];
              const milestones = typeof ph === "object" && Array.isArray(ph.milestones) ? ph.milestones : [];

              return (
                <div key={idx} className="phase-card">
                  <div className="phase-header">
                    <span className="phase-badge">STAGE 0{idx + 1}</span>
                    {duration && <span className="phase-duration">{duration}</span>}
                  </div>
                  <h5 className="phase-name">{name}</h5>
                  {objs.length > 0 && (
                    <div className="phase-goals">
                      <span className="phase-goal-label">OBJECTIVES:</span>
                      <ul>
                        {objs.map((o, oi) => <li key={oi}>{o}</li>)}
                      </ul>
                    </div>
                  )}
                  {milestones.length > 0 && (
                    <div className="phase-milestones">
                      <span className="phase-goal-label">EXIT MILESTONES:</span>
                      <ul>
                        {milestones.map((m, mi) => <li key={mi}>{m}</li>)}
                      </ul>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {key_metrics && key_metrics.length > 0 && (
        <div className="key-metrics-container">
          <h4 className="sub-section-title">TRACTION & VALIDATION KPIS</h4>
          <div className="metrics-dashboard-grid">
            {key_metrics.map((km, idx) => {
              const metric = typeof km === "string" ? km : km.metric || "Metric";
              const target = typeof km === "object" ? km.target : null;
              const timeframe = typeof km === "object" ? km.timeframe : null;

              return (
                <div key={idx} className="traction-metric-card">
                  <div className="metric-header">
                    <span className="metric-idx">KPI 0{idx + 1}</span>
                    {timeframe && <span className="metric-timeframe">{timeframe}</span>}
                  </div>
                  <div className="metric-name">{metric}</div>
                  {target && (
                    <div className="metric-target-box">
                      <span className="target-label">TARGET:</span> {target}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
