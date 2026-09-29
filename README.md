# EazyOut Lead Generation System

## Live Landing Page
https://wheelercameron193-hub.github.io/eazyout-leads-landing/

## Setup Instructions (5 minutes)

### 1. Get an Email API Key
Sign up for a free email service (any of these):
- **Brevo** (300 emails/day free): https://get.brevo.com/register
- **Resend** (1000 emails/month free): https://resend.com/signup
- **SMTP2GO** (1000 emails/month free): https://www.smtp2go.com/signup

### 2. Add Secrets to GitHub
Go to: https://github.com/wheelercameron193-hub/eazyout-leads-landing/settings/secrets/actions

Add these secrets:
- `RESEND_API_KEY` (or `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`)
- `FROM_EMAIL` (e.g., `The EazyOut Team <team@eazy-out.com>`)
- `EMAIL_PROVIDER` = `resend` (or `smtp`)

### 3. How It Works
- FormSubmit captures emails from the landing page → forwarded to your email
- Add leads to `email-automation/leads.csv`
- GitHub Action runs daily at 9 AM UTC, sends nurture emails based on signup date
- Each lead gets 7 emails over 7 days (playbook → exit strategy → $499 offer)

### 4. Update FormSubmit Email
In `index.html`, replace `Mr.wheeler2021@gmail.com` in the form action with your email.

### 5. Community Engagement
Answers are in `community/current-questions-answers.md` — post these on Reddit (r/TimeshareOwners), Quora, and TUG forums.
