"""
CYBERMON Notifier v8
━━━━━━━━━━━━━━━━━━━━
Daily PDF report at end of simulation (23:59:59).
No per-alert emails. One clean report per simulated day.

To enable email sending, set in docker-compose.yml:
  SMTP_USER: your@gmail.com
  SMTP_PASS: your-app-password   (from myaccount.google.com/apppasswords)
  ALERT_EMAIL: recipient@email.com
"""
import logging
import io
from datetime import datetime, timezone

logger = logging.getLogger("notifier")


# ── PDF Generation (pure Python, no external PDF lib needed) ──────────────────
def generate_daily_report_html(stats: dict) -> str:
    """Generate a self-contained HTML report (printable as PDF via browser)."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    cats = stats.get("categories", {})
    top5 = stats.get("top_countries", [])
    alerts = stats.get("recent_alerts", [])

    rows_cats = "".join(
        f"<tr><td>{c}</td><td>{v}</td></tr>"
        for c, v in cats.items()
    )
    rows_top5 = "".join(
        f"<tr><td>{c['code']}</td><td>{c['count']:,}</td><td>{c['avg_risk']}</td></tr>"
        for c in top5
    )
    rows_alerts = "".join(
        f"<tr><td>{a.get('level','')}</td><td>{a.get('message','')[:80]}</td><td>{a.get('ip','')}</td></tr>"
        for a in alerts[:20]
    )

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"/>
<title>CYBERMON Daily Report — {now}</title>
<style>
  body{{font-family:monospace;background:#0b1326;color:#dae2fd;padding:32px;max-width:900px;margin:auto}}
  h1{{color:#adc6ff;letter-spacing:4px;border-bottom:1px solid #424754;padding-bottom:12px}}
  h2{{color:#4edea3;font-size:13px;letter-spacing:2px;text-transform:uppercase;margin-top:28px}}
  table{{border-collapse:collapse;width:100%;font-size:12px;margin-top:8px}}
  th{{background:#171f33;color:#8c909f;padding:8px 12px;text-align:left;text-transform:uppercase;font-size:10px;letter-spacing:1px}}
  td{{padding:8px 12px;border-bottom:1px solid #2d3449;color:#c2c6d6}}
  .kpi{{display:inline-block;background:#171f33;border:1px solid #2d3449;border-radius:8px;padding:16px 24px;margin:8px;min-width:160px}}
  .kpi-val{{font-size:28px;font-weight:bold;color:#adc6ff}}
  .kpi-label{{font-size:10px;color:#8c909f;text-transform:uppercase;letter-spacing:1px}}
  .badge-crit{{color:#ffb4ab}} .badge-atk{{color:#ffb3ad}} .badge-susp{{color:#adc6ff}} .badge-norm{{color:#4edea3}}
  @media print{{body{{background:white;color:#111}} h1,h2{{color:#003}} th{{background:#eee;color:#555}} td{{color:#333}} .kpi{{background:#f5f5f5}}}}
</style></head>
<body>
<h1>🛡️ CYBERMON — DAILY SIMULATION REPORT</h1>
<p style="color:#64748b;font-size:11px">Generated: {now} | Simulated period: 00:00:00 → 23:59:59</p>

<div style="margin:20px 0">
  <div class="kpi"><div class="kpi-val">{stats.get('total_events',0):,}</div><div class="kpi-label">Total Events</div></div>
  <div class="kpi"><div class="kpi-val" style="color:#ffb3ad">{stats.get('active_alerts',0)}</div><div class="kpi-label">Active Alerts</div></div>
  <div class="kpi"><div class="kpi-val" style="color:#4edea3">{stats.get('blocked_ips',0)}</div><div class="kpi-label">Blocked IPs</div></div>
  <div class="kpi"><div class="kpi-val" style="color:#d8e2ff">{stats.get('avg_risk',0):.1f}</div><div class="kpi-label">Avg Risk Score</div></div>
</div>

<h2>Event Distribution</h2>
<table><tr><th>Category</th><th>Count</th></tr>{rows_cats}</table>

<h2>Top Source Geographies</h2>
<table><tr><th>Country</th><th>Events</th><th>Avg Risk</th></tr>{rows_top5}</table>

<h2>Recent Alerts (last 20)</h2>
<table><tr><th>Level</th><th>Message</th><th>IP</th></tr>{rows_alerts}</table>

<p style="margin-top:40px;color:#424754;font-size:10px;border-top:1px solid #2d3449;padding-top:16px">
© CYBERMON Sentinel Protocol — Auto-generated end-of-day report
</p>
</body></html>"""


async def send_daily_report(stats: dict):
    """
    Called at simulation end (23:59:59).
    Sends the HTML report by email if SMTP is configured.
    Otherwise just logs it.
    """
    from src.config.settings import settings

    html = generate_daily_report_html(stats)

    if not settings.SMTP_USER or not settings.SMTP_PASS:
        logger.info(
            "Daily report generated (email disabled — configure SMTP_USER and SMTP_PASS "
            "in docker-compose.yml to enable). Report length: %d chars", len(html)
        )
        return

    try:
        import aiosmtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[CYBERMON] Daily Simulation Report — {datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
        msg["From"]    = settings.SMTP_USER
        msg["To"]      = settings.ALERT_EMAIL
        msg.attach(MIMEText(html, "html"))

        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASS,
            start_tls=True,
        )
        logger.info("Daily report sent to %s", settings.ALERT_EMAIL)
    except Exception as e:
        logger.error("Failed to send daily report: %s", e)


# Per-alert email is DISABLED — only daily reports
async def send_critical_alert(alert: dict):
    """No-op: per-alert emails replaced by daily report."""
    pass
