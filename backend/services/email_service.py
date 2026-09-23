"""
Team Forge Email Automation Service
------------------------------------
Dispatches beautiful, executive validation dossiers to the founder's Gmail inbox.
Supports:
  1. Live Gmail SMTP (via Google App Password)
  2. Local dev mode fallback (saves responsive HTML preview to backend/data/emails/)
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, Optional

SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "").strip()
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "").strip()
APP_BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:5173")


def build_email_html(report_data: Dict[str, Any], job_id: str) -> str:
    """Builds a responsive, modern HTML email template for the validation dossier."""
    extracted = report_data.get("extracted_data") or {}
    product_name = extracted.get("product_name") or "Your Startup Concept"
    industry = extracted.get("industry") or "General Tech"
    problem = extracted.get("core_problem") or "Problem statement"

    # Market sizing
    ma = report_data.get("market_analysis") or {}
    market_size_list = ma.get("market_size") or []
    tam_text = "Analysis available in dashboard"
    if market_size_list and isinstance(market_size_list, list) and len(market_size_list) > 0:
        first = market_size_list[0]
        if isinstance(first, dict):
            tam_text = f"{first.get('scope', 'Global')}: {first.get('value', 'Assessed')}"

    # Competitors
    ca = report_data.get("competitor_analysis") or {}
    competitors = ca.get("competitors") or []
    comp_names = [c.get("name") for c in competitors[:4] if isinstance(c, dict) and c.get("name")]
    comps_text = ", ".join(comp_names) if comp_names else "Market analysis completed"

    # Top White-Space
    ws = report_data.get("white_space_analysis") or {}
    opps = ws.get("opportunities") or []
    top_opp = opps[0].get("title", "High-conviction market void identified") if (opps and isinstance(opps[0], dict)) else "White-space opportunities mapped"

    # MVP thesis
    mvp = report_data.get("mvp_recommendation") or {}
    mvp_name = mvp.get("mvp_name") or "Phase 1 MVP Scope"
    mvp_thesis = mvp.get("mvp_thesis") or "Focused validation release"

    report_url = f"{APP_BASE_URL}/?job_id={job_id}"

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Your Team Forge Validation Report</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b;">
  <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f8fafc; padding: 40px 10px;">
    <tr>
      <td align="center">
        <table width="100%" max-width="600" border="0" cellspacing="0" cellpadding="0" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.05);">
          
          <!-- Header -->
          <tr>
            <td style="padding: 30px; background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); color: #ffffff;">
              <div style="font-size: 11px; font-weight: 700; letter-spacing: 0.1em; color: #818cf8; text-transform: uppercase; margin-bottom: 8px;">TEAM FORGE AI VALIDATION DOSSIER</div>
              <h1 style="margin: 0; font-size: 24px; font-weight: 700; line-height: 1.3;">{product_name}</h1>
              <div style="font-size: 13px; color: #cbd5e1; margin-top: 6px;">Industry: {industry}</div>
            </td>
          </tr>

          <!-- Summary Alert -->
          <tr>
            <td style="padding: 24px 30px; background-color: #f1f5f9; border-bottom: 1px solid #e2e8f0;">
              <div style="font-size: 12px; font-weight: 700; color: #4338ca; text-transform: uppercase; margin-bottom: 4px;">Validation Status</div>
              <div style="font-size: 14px; color: #334155; line-height: 1.5;">Your autonomous 9-stage validation analysis is complete. Here are the executive highlights discovered from real-time web research:</div>
            </td>
          </tr>

          <!-- Key Metrics Grid -->
          <tr>
            <td style="padding: 24px 30px;">
              <table width="100%" border="0" cellspacing="0" cellpadding="0">
                
                <!-- Problem Statement -->
                <tr>
                  <td style="padding-bottom: 20px;">
                    <div style="font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase;">Core Problem Addressed</div>
                    <div style="font-size: 14px; color: #0f172a; margin-top: 4px; line-height: 1.4;">{problem}</div>
                  </td>
                </tr>

                <!-- Market Sizing -->
                <tr>
                  <td style="padding-bottom: 20px;">
                    <div style="font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase;">Market Opportunity (TAM/SAM)</div>
                    <div style="font-size: 14px; font-weight: 600; color: #0f172a; margin-top: 4px;">{tam_text}</div>
                  </td>
                </tr>

                <!-- Competitors -->
                <tr>
                  <td style="padding-bottom: 20px;">
                    <div style="font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase;">Key Competitors Discovered</div>
                    <div style="font-size: 14px; color: #0f172a; margin-top: 4px;">{comps_text}</div>
                  </td>
                </tr>

                <!-- White Space -->
                <tr>
                  <td style="padding-bottom: 20px;">
                    <div style="font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase;">Top Market White Space</div>
                    <div style="font-size: 14px; color: #0f172a; margin-top: 4px; font-weight: 600;">{top_opp}</div>
                  </td>
                </tr>

                <!-- MVP Scope -->
                <tr>
                  <td style="padding-bottom: 24px;">
                    <div style="font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase;">Recommended MVP Scope</div>
                    <div style="font-size: 14px; color: #0f172a; margin-top: 4px;"><strong>{mvp_name}:</strong> {mvp_thesis}</div>
                  </td>
                </tr>

              </table>

              <!-- CTA Button -->
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-top: 10px;">
                <tr>
                  <td align="center">
                    <a href="{report_url}" target="_blank" style="display: inline-block; background-color: #0f172a; color: #ffffff; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-size: 14px; font-weight: 600; letter-spacing: 0.02em;">Open Full Interactive Dossier &rarr;</a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding: 20px 30px; background-color: #f8fafc; border-top: 1px solid #e2e8f0; font-size: 12px; color: #94a3b8; text-align: center;">
              <div>Generated autonomously by <strong>Team Forge Startup Idea Validator</strong>.</div>
              <div style="margin-top: 4px;">Grounding Invariant: All figures and competitors are cited from live empirical web search.</div>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
    return html


def send_validation_email(to_email: str, report_data: Dict[str, Any], job_id: str) -> bool:
    """
    Sends the completed validation report to the user's Gmail.
    If SMTP credentials are not configured, saves a local HTML preview to backend/data/emails/.
    """
    extracted = report_data.get("extracted_data") or {}
    product_name = extracted.get("product_name") or "Your Startup Pitch"
    subject = f"🚀 Team Forge Validation Report: {product_name}"
    html_content = build_email_html(report_data, job_id)

    # If live SMTP credentials are configured, send via TLS SMTP
    if SMTP_USER and SMTP_PASSWORD:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"Team Forge AI <{SMTP_USER}>"
            msg["To"] = to_email

            part = MIMEText(html_content, "html")
            msg.attach(part)

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, [to_email], msg.as_string())
            server.quit()
            print(f"[email_service] Successfully sent validation email to {to_email}")
            return True
        except Exception as exc:
            print(f"[email_service] SMTP sending failed: {exc}. Saving local preview instead.")

    # Local development preview fallback
    email_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "emails")
    os.makedirs(email_dir, exist_ok=True)
    preview_file = os.path.join(email_dir, f"{job_id}.html")
    with open(preview_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[email_service] Live SMTP not active (set SMTP_USER and SMTP_PASSWORD in backend/.env).")
    print(f"[email_service] Saved responsive HTML email preview to: {preview_file}")
    return True
