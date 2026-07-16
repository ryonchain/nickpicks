# Playwright Outreach Form Submission Tool

## Overview

This tool automates submitting your outreach pitch to business contact forms.  
It handles JS-rendered forms that server-side POST requests can't reach, and automatically detects and skips reCAPTCHA-protected sites (tagging them as `email-only` so you can route them through Gmail).

---

## Setup (one-time)

```bash
pip install playwright
playwright install chromium
```

---

## Input CSV Format

Create a CSV file with these columns:

| Column | Description |
|---|---|
| `business_name` | The business name (used to fill "name" fields) |
| `form_url` | Direct URL to the contact/inquiry form page |
| `pitch_text` | The message body to submit |

**Example (`wave17_prospects.csv`):**
```csv
business_name,form_url,pitch_text
"Acme Studio","https://acmestudio.com/contact","Hi, I'm reaching out from Nick Company..."
"Blue Oak Design","https://blueoakdesign.com/get-in-touch","Hi, I'm reaching out..."
```

---

## Running the Tool

### Default (visible browser — recommended for first run)

```bash
python3 scripts/submit_forms.py wave17_prospects.csv
```

### Headless mode (faster, no browser window)

```bash
python3 scripts/submit_forms.py wave17_prospects.csv --headless
```

### Full options

```bash
python3 scripts/submit_forms.py wave17_prospects.csv \
  --output submission_results.csv \
  --headless \
  --timeout 30 \
  --email hello@nickcompany.com \
  --slow-mo 100
```

| Flag | Default | Description |
|---|---|---|
| `--output` | `submission_results.csv` | Where to write results |
| `--headless` | off (visible) | Run without browser window |
| `--timeout` | 30 | Seconds to wait per site |
| `--email` | `hello@nickcompany.com` | Email address to fill in forms |
| `--slow-mo` | 100 | Ms delay between actions (visible mode only) |

---

## Output CSV

Results are saved to `submission_results.csv` with these columns:

| Column | Values | Meaning |
|---|---|---|
| `status` | `success` | Form submitted; confirmation detected |
| | `uncertain` | Form submitted; no confirmation message (still likely delivered) |
| | `email-only` | **reCAPTCHA detected — route via Gmail instead** |
| | `failed` | Could not submit (timeout, no form found, etc.) |
| | `skipped` | Missing URL in input |
| `reason` | text | Specific reason for the status |
| `timestamp` | ISO 8601 | When the submission was attempted |

---

## Workflow

1. CMO provides `wave17_prospects.csv` with blocked businesses from Wave 16
2. Run the tool (visible mode first to spot-check behavior)
3. Review `submission_results.csv`:
   - `success` / `uncertain` → submitted, track for replies
   - `email-only` → route through Gmail once OAuth is live (see [NIC-836])
   - `failed` → investigate individually (check the URL manually)

---

## reCAPTCHA Policy

The tool **never attempts to solve or bypass CAPTCHAs**.  
When a CAPTCHA is detected, the site is tagged `email-only` and skipped.  
These businesses need manual Gmail outreach once Google OAuth is configured.

---

## Troubleshooting

**"No fillable fields found"** — The form may not have loaded. Try running without `--headless` to watch what happens.

**"Page load timeout"** — Increase `--timeout 60` for slow sites.

**Submission looks correct but status is `uncertain`** — The site submitted fine but doesn't show a visible thank-you message. Check manually by visiting the URL; most CRMs still deliver the message.

**Playwright not installed** — Run `pip install playwright && playwright install chromium`.
