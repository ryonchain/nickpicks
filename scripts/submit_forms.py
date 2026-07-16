#!/usr/bin/env python3
"""
Playwright-based contact form submission tool for Wave 17+ outreach.

Usage:
    python3 scripts/submit_forms.py input.csv [--headless] [--output results.csv] [--timeout 30]

Input CSV columns: business_name, form_url, pitch_text
Output CSV columns: business_name, form_url, status, reason, timestamp
"""

import asyncio
import csv
import argparse
import sys
from datetime import datetime
from pathlib import Path

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("ERROR: Playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)


# CAPTCHA signals — any match means skip this site
CAPTCHA_SIGNALS = [
    "recaptcha",
    "g-recaptcha",
    "grecaptcha",
    "hcaptcha",
    "h-captcha",
    "cf-turnstile",
    "challenges.cloudflare.com",
    "captcha.js",
    "/_Incapsula_Resource",
    "datadome",
    "funcaptcha",
    "arkoselabs",
]

# Success indicators in page content after submission
SUCCESS_SIGNALS = [
    "thank you",
    "thanks for",
    "message sent",
    "message received",
    "we'll be in touch",
    "we will be in touch",
    "we got your",
    "submission received",
    "successfully submitted",
    "your inquiry",
    "your message has been",
    "contact us soon",
    "get back to you",
]

# Ordered selector groups: (label, selectors_list)
# We try each group's selectors in order; first match wins.
FIELD_SELECTOR_GROUPS = {
    "name": [
        'input[autocomplete="name"]',
        'input[name="name"]',
        'input[name="full_name"]',
        'input[name="fullname"]',
        'input[name="your-name"]',
        'input[id*="name" i]:not([id*="company" i]):not([id*="last" i])',
        'input[placeholder*="your name" i]',
        'input[placeholder*="full name" i]',
        'input[placeholder*="first name" i]',
        'input[aria-label*="name" i]:not([aria-label*="company" i])',
    ],
    "email": [
        'input[type="email"]',
        'input[name*="email" i]',
        'input[id*="email" i]',
        'input[placeholder*="email" i]',
        'input[autocomplete="email"]',
    ],
    "subject": [
        'input[name*="subject" i]',
        'input[id*="subject" i]',
        'input[placeholder*="subject" i]',
        'input[aria-label*="subject" i]',
    ],
    "phone": [
        'input[type="tel"]',
        'input[name*="phone" i]',
        'input[id*="phone" i]',
        'input[placeholder*="phone" i]',
    ],
    "message": [
        'textarea[name*="message" i]',
        'textarea[id*="message" i]',
        'textarea[placeholder*="message" i]',
        'textarea[name*="comment" i]',
        'textarea[name*="body" i]',
        'textarea[aria-label*="message" i]',
        "textarea",  # fallback: any textarea
    ],
}

SUBMIT_SELECTORS = [
    'button[type="submit"]',
    'input[type="submit"]',
    'button:has-text("Send")',
    'button:has-text("Submit")',
    'button:has-text("Contact")',
    'button:has-text("Send Message")',
    'button:has-text("Get in Touch")',
    '[role="button"][aria-label*="submit" i]',
]


def detect_captcha(html: str) -> bool:
    lower = html.lower()
    return any(signal in lower for signal in CAPTCHA_SIGNALS)


def detect_success(html: str) -> bool:
    lower = html.lower()
    return any(signal in lower for signal in SUCCESS_SIGNALS)


async def fill_field(page, selectors: list[str], value: str, field_label: str) -> bool:
    """Try selectors in order; fill first visible, enabled match. Returns True if filled."""
    for sel in selectors:
        try:
            elements = await page.query_selector_all(sel)
            for el in elements:
                if await el.is_visible() and await el.is_enabled():
                    await el.click()
                    await el.fill(value)
                    return True
        except Exception:
            continue
    return False


async def submit_form(page, timeout_ms: int) -> str:
    """Click submit button; return 'submitted' or error message."""
    for sel in SUBMIT_SELECTORS:
        try:
            btn = await page.query_selector(sel)
            if btn and await btn.is_visible() and await btn.is_enabled():
                await btn.click()
                return "submitted"
        except Exception:
            continue
    return "no_submit_button_found"


async def process_url(
    context,
    business_name: str,
    form_url: str,
    pitch_text: str,
    sender_email: str,
    timeout_sec: int,
) -> dict:
    timeout_ms = timeout_sec * 1000
    result = {
        "business_name": business_name,
        "form_url": form_url,
        "status": "unknown",
        "reason": "",
        "timestamp": datetime.utcnow().isoformat(),
    }

    page = await context.new_page()
    try:
        # Navigate
        try:
            await page.goto(form_url, timeout=timeout_ms, wait_until="domcontentloaded")
        except PlaywrightTimeout:
            result["status"] = "failed"
            result["reason"] = "page_load_timeout"
            return result
        except Exception as e:
            result["status"] = "failed"
            result["reason"] = f"navigation_error: {e}"
            return result

        # Wait for the page to settle a bit
        await page.wait_for_timeout(2000)

        # Check for CAPTCHA
        html = await page.content()
        if detect_captcha(html):
            result["status"] = "email-only"
            result["reason"] = "recaptcha_detected"
            return result

        # Try to fill fields
        filled_email = await fill_field(page, FIELD_SELECTOR_GROUPS["email"], sender_email, "email")
        filled_name = await fill_field(page, FIELD_SELECTOR_GROUPS["name"], business_name, "name")
        filled_message = await fill_field(page, FIELD_SELECTOR_GROUPS["message"], pitch_text, "message")
        filled_subject = await fill_field(page, FIELD_SELECTOR_GROUPS["subject"], "Partnership Inquiry", "subject")

        # Phone fields — leave blank unless the page requires them (we skip if required later)
        # Don't fill phone — avoid appearing as spam and reduce friction

        if not filled_email and not filled_message:
            result["status"] = "failed"
            result["reason"] = "no_fillable_fields_found"
            return result

        if not filled_message:
            result["status"] = "failed"
            result["reason"] = "no_message_field_found"
            return result

        # Submit
        pre_submit_url = page.url
        submit_result = await submit_form(page, timeout_ms)

        if submit_result != "submitted":
            result["status"] = "failed"
            result["reason"] = submit_result
            return result

        # Wait for navigation or success signal
        try:
            await page.wait_for_load_state("networkidle", timeout=timeout_ms)
        except PlaywrightTimeout:
            pass  # Not all sites trigger navigation; check content anyway

        await page.wait_for_timeout(2000)

        post_html = await page.content()
        post_url = page.url

        # Check for CAPTCHA wall that appeared after submit
        if detect_captcha(post_html):
            result["status"] = "email-only"
            result["reason"] = "recaptcha_appeared_post_submit"
            return result

        # Check success
        if detect_success(post_html) or post_url != pre_submit_url:
            result["status"] = "success"
            result["reason"] = "success_signal_detected" if detect_success(post_html) else "url_changed_after_submit"
        else:
            result["status"] = "uncertain"
            result["reason"] = "submitted_but_no_success_signal"

    except Exception as e:
        result["status"] = "failed"
        result["reason"] = f"unexpected_error: {e}"
    finally:
        await page.close()

    return result


async def run(
    input_csv: str,
    output_csv: str,
    headless: bool,
    timeout_sec: int,
    sender_email: str,
    slow_mo: int,
) -> None:
    # Read input
    rows = []
    with open(input_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    if not rows:
        print("No rows found in input CSV.")
        return

    print(f"Loaded {len(rows)} businesses from {input_csv}")
    print(f"Mode: {'headless' if headless else 'visible'} | Timeout: {timeout_sec}s per site")
    print(f"Output: {output_csv}")
    print()

    results = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=headless, slow_mo=slow_mo if not headless else 0)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="en-US",
            viewport={"width": 1280, "height": 800},
        )

        for i, row in enumerate(rows, 1):
            business_name = row.get("business_name", "").strip()
            form_url = row.get("form_url", "").strip()
            pitch_text = row.get("pitch_text", "").strip()

            if not form_url:
                results.append({
                    "business_name": business_name,
                    "form_url": form_url,
                    "status": "skipped",
                    "reason": "missing_url",
                    "timestamp": datetime.utcnow().isoformat(),
                })
                print(f"[{i}/{len(rows)}] {business_name}: SKIPPED (missing URL)")
                continue

            print(f"[{i}/{len(rows)}] {business_name}: {form_url}")
            result = await process_url(
                context, business_name, form_url, pitch_text, sender_email, timeout_sec
            )
            results.append(result)

            status_icon = {
                "success": "✓",
                "email-only": "⚠",
                "failed": "✗",
                "uncertain": "?",
                "skipped": "-",
            }.get(result["status"], "?")
            print(f"  {status_icon} {result['status'].upper()}: {result['reason']}")

        await browser.close()

    # Write output
    fieldnames = ["business_name", "form_url", "status", "reason", "timestamp"]
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Summary
    from collections import Counter
    counts = Counter(r["status"] for r in results)
    print()
    print("=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"  Total:      {len(results)}")
    print(f"  Success:    {counts.get('success', 0)}")
    print(f"  Uncertain:  {counts.get('uncertain', 0)}  (submitted; no confirmation)")
    print(f"  Email-only: {counts.get('email-only', 0)}  (reCAPTCHA — route via Gmail)")
    print(f"  Failed:     {counts.get('failed', 0)}")
    print(f"  Skipped:    {counts.get('skipped', 0)}")
    print(f"\nResults saved to: {output_csv}")


def main():
    parser = argparse.ArgumentParser(
        description="Submit outreach forms via Playwright. Input CSV: business_name, form_url, pitch_text"
    )
    parser.add_argument("input", help="Path to input CSV (business_name, form_url, pitch_text)")
    parser.add_argument(
        "--output",
        default="submission_results.csv",
        help="Path for output CSV (default: submission_results.csv)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=False,
        help="Run in headless mode (default: visible browser for debugging)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout in seconds per site (default: 30)",
    )
    parser.add_argument(
        "--email",
        default="hello@nickcompany.com",
        help="Sender email to fill in contact forms",
    )
    parser.add_argument(
        "--slow-mo",
        type=int,
        default=100,
        dest="slow_mo",
        help="Slow down visible browser by N ms per action (default: 100, ignored in headless mode)",
    )
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"ERROR: Input file not found: {args.input}")
        sys.exit(1)

    asyncio.run(
        run(
            input_csv=args.input,
            output_csv=args.output,
            headless=args.headless,
            timeout_sec=args.timeout,
            sender_email=args.email,
            slow_mo=args.slow_mo,
        )
    )


if __name__ == "__main__":
    main()
