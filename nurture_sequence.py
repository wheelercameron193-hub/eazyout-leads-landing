#!/usr/bin/env python3
"""
EazyOut Lead Nurture Automation
Sends the 7-day email sequence to new leads.

Usage:
  Run this script daily via cron or GitHub Actions.
  It reads leads from leads.csv, checks their signup date,
  and sends the appropriate email from the nurture sequence.

Requirements:
  pip install resend  (or set EMAIL_PROVIDER=smtp)
  
  Environment variables:
  EMAIL_PROVIDER: "resend" or "smtp"
  RESEND_API_KEY: Resend API key (if using resend)
  SMTP_SERVER: SMTP host (if using smtp)
  SMTP_PORT: SMTP port
  SMTP_USER: SMTP username
  SMTP_PASS: SMTP password
  FROM_EMAIL: Sender email address
"""
import csv
import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent
LEADS_FILE = BASE_DIR / "leads.csv"
STATE_FILE = BASE_DIR / "email_state.json"
EMAILS_FILE = BASE_DIR / "nurture_sequence_emails.json"

# The 7-day nurture sequence content
NURTURE_EMAILS = {
    0: {
        "subject": "Your Timeshare Exit Playbook is inside",
        "body": """Welcome to EazyOut!

Your free Timeshare Exit Playbook is attached. This 7-step guide walks you through:
- How to cancel within the rescission window (no lawyer needed)
- How to write cancellation letters that actually work
- How to spot and avoid exit scams
- Developer-specific exit programs (Wyndham, Marriott, Hilton, etc.)

Tomorrow you'll receive Day 1 of our email sequence with your first action step.

Stay organized,
The EazyOut Team"""
    },
    1: {
        "subject": "Day 1: Check Your Rescission Window",
        "body": """If you bought your timeshare in the last 3-10 days, you have a legal right to cancel for FREE. This is called the "rescission period."

Your first step: Find the rescission clause in your contract. It's usually near the end. The law requires it to be in bold or underlined.

If you're within this window:
1. Write a cancellation letter (use Template A from the playbook)
2. Send it via certified mail with return receipt
3. Keep the receipt — this is your proof of delivery

If you're PAST the window:
Don't panic. There are still legitimate exit paths. Tomorrow we'll cover how to identify which path works for your situation.

Reply to this email if you need help finding the rescission clause in your contract.

— The EazyOut Team"""
    },
    2: {
        "subject": "Day 2: Which Exit Path Is Right for You?",
        "body": """Not all timeshare exits are the same. The right path depends on your specific situation.

Quick decision tree:
- **Recent purchase (0-10 days)** → Rescission cancel (you're in the easiest path)
- **Paid in full, fees current** → Developer deed-back program ($100-500)
- **Behind on payments, small balance** → Settlement negotiation (pay less to close)
- **Large balance, behind on payments** → Hardship program + payment plan
- **Fraud or misrepresentation** → Legal action (start with $200-500 lawyer consult)
- **Inherited** → Disclaimer of interest or gift to family member

Most people waste time on the wrong path. Use the Decision Matrix in the playbook to identify yours.

Tomorrow: How to write the letters that actually get results.

— The EazyOut Team"""
    },
    3: {
        "subject": "Day 3: Write Letters That Get Results",
        "body": """Generic letters get ignored. Developer-specific letters get responses.

**Template A (Rescission):** Must use the exact language from your contract's cancellation clause. Copy-paste, don't paraphrase.

**Template B (Deed-Back):** Key phrase — "I am voluntarily surrendering all rights, title, and interest." Do NOT say "cancel" or "refund."

**Template C (Maintenance Fee Dispute):** "I dispute the maintenance fees due to [health/financial hardship]. I request a hardship deferral and payment plan."

Pro tip: Always send BOTH certified mail AND email a PDF copy to the developer's owner services department. The certified mail establishes your legal position. The email creates a paper trail they can't ignore.

Tomorrow: How to handle the financial complications that stop most people.

— The EazyOut Team"""
    },
    4: {
        "subject": "Day 4: Protect Your Credit While Exiting",
        "body": """Stopping payments feels tempting, but it ruins your credit for 7 years. Here's the smart approach:

1. **Stay current while negotiating** — Call the resort and say: "I'm pursuing an exit. Can I make reduced payments while the process completes?"

2. **Document everything** — Get any agreement in writing. "Verbal promises" mean nothing to collection agencies.

3. **Negotiate a settlement** — Most resorts will accept 30-50% of the balance if you offer a lump sum. Write: "I can pay $X as full settlement. Please confirm in writing that this settles the account."

4. **Payment plans** — If you can't pay a lump sum, ask for a monthly payment plan. Most resorts prefer $25/month from you over $0/month and a foreclosure.

5. **Hardship programs** — Every major resort has one. Ask: "Do you offer a COVID-19 style hardship deferral?"

The key phrase: "I am actively pursuing an exit. What payment arrangement can you offer while I complete the process?"

— The EazyOut Team"""
    },
    5: {
        "subject": "Day 5: Spot & Avoid Exit Scams",
        "body": """The timeshare exit industry has one of the worst scam rates in consumer services. Here's your survival checklist:

RED FLAGS (Run away):
- Charges large upfront fees ($1,000+)
- Won't put terms in writing
- Can't explain the legal process
- ALL reviews are positive (no negatives)
- Claims "insider connections" at your resort
- Says process takes "6-8 weeks"

GREEN FLAGS (Trustworthy):
- Charges a reasonable, transparent fee
- Has a clear refund policy
- Provides references you can call
- Has a physical address and verifiable registration
- Doesn't ask you to stop paying the resort
- Explains risks honestly
- Money-back guarantee

If an exit company contacts you, verify them first: search their name + "scam" or "complaint" on the BBB and Google.

Need help evaluating an exit company? Reply to this email with their name and I'll check them for you.

— The EazyOut Team"""
    },
    7: {
        "subject": "Day 7: Ready for Full Access?",
        "body": """If you've been following this sequence, you now have:
✓ Your rescission window checked
✓ Your exit path identified
✓ Your cancellation letters written
✓ Financial protection strategy
✓ Scam avoidance knowledge

Now, here's what most people miss: Organization. Keeping track of 50+ documents, multiple deadlines, certified mail receipts, and phone calls.

That's what EazyOut Full Access ($499) helps with. It's NOT a service that acts for you — it's software that helps YOU stay organized through the process.

What's included:
- Document tracker (never lose a receipt)
- Deadline calendar (never miss a rescission window)
- Letter generator (auto-fills your contract details)
- Progress dashboard (see where you are in the process)
- Email reminder system (never forget to follow up)

We offer a 14-day money-back guarantee. No questions asked.

If you're ready to stay organized through your exit: {upgrade_link}

If you're handling it solo, that's fine too. You now have everything you need.

— The EazyOut Team"""
    },
}

def send_email_smtp(to_email, subject, body):
    """Send email via SMTP."""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    from_email = os.environ.get("FROM_EMAIL", smtp_user)

    if not smtp_user or not smtp_pass:
        print(f"ERROR: SMTP credentials not set. Skipping email to {to_email}")
        return False

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        print(f"Sent via SMTP: {to_email} - {subject}")
        return True
    except Exception as e:
        print(f"SMTP error sending to {to_email}: {e}")
        return False

def send_email_resend(to_email, subject, body):
    """Send email via Resend API."""
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        print(f"ERROR: RESEND_API_KEY not set. Skipping email to {to_email}")
        return False

    try:
        import resend
        resend.api_key = api_key
        r = resend.emails.send({
            "from": os.environ.get("FROM_EMAIL", "EazyOut Team <hello@eazyout.ai>"),
            "to": to_email,
            "subject": subject,
            "text": body,
        })
        print(f"Sent via Resend: {to_email} - {subject}")
        return True
    except Exception as e:
        print(f"Resend error sending to {to_email}: {e}")
        return False

def load_state():
    """Load email state from file."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}

def save_state(state):
    """Save email state to file."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def load_leads():
    """Load leads from CSV file."""
    leads = []
    if not LEADS_FILE.exists():
        # Create sample leads file
        with open(LEADS_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "email", "signup_date", "source"])
        return leads

    with open(LEADS_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            leads.append(row)
    return leads

def send_email(to_email, subject, body):
    """Send email using the configured provider."""
    provider = os.environ.get("EMAIL_PROVIDER", "resend")
    if provider == "smtp":
        return send_email_smtp(to_email, subject, body)
    else:
        return send_email_resend(to_email, subject, body)

def main():
    leads = load_leads()
    state = load_state()
    today = datetime.now()

    for lead in leads:
        email = lead["email"]
        signup_date_str = lead.get("signup_date", "")
        if not signup_date_str:
            continue

        signup_date = datetime.fromisoformat(signup_date_str)
        days_since_signup = (today - signup_date).days

        # Check if we should send an email today
        if days_since_signup in NURTURE_EMAILS:
            email_key = f"{email}:{days_since_signup}"
            if email_key not in state:
                # Send the email
                email_content = NURTURE_EMAILS[days_since_signup]
                success = send_email(
                    email,
                    email_content["subject"],
                    email_content["body"]
                )
                if success:
                    state[email_key] = {"sent_at": today.isoformat(), "day": days_since_signup}

    save_state(state)
    print(f"Processed {len(leads)} leads. Emails sent: {sum(1 for v in state.values() if 'sent_at' in v)}")

if __name__ == "__main__":
    main()
