# Password reset

The app supports **Forgot password** from the login screen. Flow:

1. User taps **Forgot password?** → enters email → receives a **6-digit code** by email.
2. User taps **I have a code — reset password** (or goes to Reset password) → enters code + new password → password is updated.

---

## What’s in place

- **Backend:** `POST /api/auth/forgot-password/` (body: `{ "email": "..." }`) and `POST /api/auth/reset-password/` (body: `{ "code": "123456", "new_password": "..." }`). Codes expire after 1 hour.
- **App:** Forgot password and Reset password screens; **Forgot password?** link on the login screen.
- **Email:** Backend sends the code by email. For that to work in **production**, you must configure email.

---

## Production: configure email

If `EMAIL_HOST` is **not** set, the backend uses the **console** backend: no real email is sent; in DEBUG the code is printed in the server log (useful for local testing only).

To send real emails (e.g. on Vercel):

1. **Set these environment variables** on your backend (Vercel project → Settings → Environment Variables):

   | Variable | Example | Notes |
   |----------|--------|--------|
   | `EMAIL_HOST` | `smtp.sendgrid.net` | SMTP server (SendGrid, Gmail, Mailgun, etc.) |
   | `EMAIL_PORT` | `587` | Usually 587 (TLS) or 465 (SSL) |
   | `EMAIL_USE_TLS` | `true` | Use TLS |
   | `EMAIL_HOST_USER` | Your SMTP username / API user | From your provider |
   | `EMAIL_HOST_PASSWORD` | Your SMTP password / API key | From your provider |
   | `DEFAULT_FROM_EMAIL` | `noreply@yourdomain.com` | Sender address (optional) |

2. **Examples:**
   - **SendGrid:** Create an API key, then `EMAIL_HOST=smtp.sendgrid.net`, `EMAIL_HOST_USER=apikey`, `EMAIL_HOST_PASSWORD=<your-api-key>`.
   - **Gmail:** Use an app password; `EMAIL_HOST=smtp.gmail.com`, port 587, TLS true.
   - **Resend / Mailgun:** They often provide SMTP credentials; use their docs.

3. **Run the new migration** on production so the `PasswordResetCode` table exists:
   - `python manage.py migrate` (with `DATABASE_URL` set to your production DB).

After that, forgot-password emails will be sent from your backend when users request a reset.
