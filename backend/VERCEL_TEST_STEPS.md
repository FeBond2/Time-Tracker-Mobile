# Test app with backend on Vercel — what you need to do

Follow these in order so the app (forgot password, login, etc.) talks to your live Vercel backend.

---

## Step 1: Push the backend to GitHub

Your Vercel project is connected to **GitHub**. The backend (including the new forgot-password and reset-password code) must be in that repo so Vercel can deploy it.

From your **project root** (the folder that contains `mobile/` and `backend/` — e.g. `TimeTrackerMobile`):

1. **See what’s changed**
   ```bash
   git status
   ```
   You should see backend files under `backend/` (e.g. `backend/core/views.py`, `backend/config/settings.py`, etc.). The `mobile/` folder may be untracked; that’s fine.

2. **Stage and commit**
   ```bash
   git add backend/
   git status
   ```
   If anything else backend-related is listed in `git status`, add it too. Do **not** add `mobile/` or `backend/.env`.

   ```bash
   git commit -m "Add forgot password and reset password; email config; migration"
   ```

3. **Push**
   ```bash
   git push origin main
   ```

4. **Wait for Vercel**  
   Go to [vercel.com](https://vercel.com) → your project. Wait until the latest deployment finishes (green check). That deploy will include the new `/api/auth/forgot-password/` and `/api/auth/reset-password/` endpoints.

---

## Step 2: Run the new migration on the production database

Vercel does **not** run Django migrations for you. You have to run them once against the database that Vercel uses.

1. **Get your production database URL**
   - Vercel dashboard → your project → **Storage** (or **Settings** / **Environment Variables**).
   - If you use **Vercel Postgres**: open the Postgres store → **.env** or **Connection string** and copy the URL (it looks like `postgres://...`).
   - If you use another host (Neon, Supabase, etc.), use that `DATABASE_URL` (or equivalent).

2. **Run migrations from your machine**
   From the **backend folder**:

   ```bash
   cd backend
   export DATABASE_URL="paste-your-production-database-URL-here"
   python3 manage.py migrate
   ```

   Use the **exact** URL from Vercel/your provider (no spaces, in quotes). This creates the `PasswordResetCode` table (and any other new tables) in production.

3. **Confirm**
   You should see something like: `Applying core.0005_add_password_reset_code... OK`

---

## Step 3: Point the app at Vercel

The app must use your **Vercel API URL** when you run it (simulator or device).

1. **Get your Vercel API URL**
   - It’s: **your Vercel project URL + `/api`**
   - Example: `https://time-tracker-mobile-xxxx.vercel.app/api`  
   (No trailing slash. Find the exact URL under your project’s **Domains** or deploy URL.)

2. **Set it for the running app**
   - **Option A — use a `.env` file (easiest for testing)**  
     In the **`mobile`** folder, create or edit `.env` so it has one line:
     ```
     EXPO_PUBLIC_API_URL=https://YOUR-VERCEL-URL.vercel.app/api
     ```
     Replace `YOUR-VERCEL-URL` with your real Vercel URL (no trailing slash after `api`).  
     Then **restart the app** (stop Expo and run `npx expo start` again from `mobile/`) so it picks up the new value.

   - **Option B — run with the URL in the command**
     From the `mobile` folder:
     ```bash
     EXPO_PUBLIC_API_URL=https://YOUR-VERCEL-URL.vercel.app/api npx expo start
     ```
     Again, replace with your real URL.

---

## Step 4: Test forgot password

1. Open the app (simulator or device) and go to **Login**.
2. Tap **Forgot password?**
3. Enter the **email** of an account that already exists (one you used to register).
4. Tap **Send reset code**.
   - If the backend is deployed and migration ran: you should get the “If an account exists…” message, and (if email is configured) an email with a 6-digit code. If email is not configured, in DEBUG the code is printed in the backend logs.
5. Tap **I have a code — reset password**, enter the code and a new password, then **Reset password**.
6. Go back to **Login** and sign in with the new password.

If you get **404**: the backend on Vercel doesn’t have the new routes yet → finish Step 1 and wait for the deploy.  
If you get **500** or other errors: check Vercel’s **Functions** or **Logs** for the backend error; often it’s a missing env var or migration not run (Step 2).

---

## Quick checklist

- [ ] Backend pushed to GitHub (`git push origin main`)
- [ ] Vercel deployment finished (green)
- [ ] Migration run on production DB (`cd backend` then `DATABASE_URL=... python3 manage.py migrate`)
- [ ] App using Vercel API URL (`mobile/.env` or `EXPO_PUBLIC_API_URL=...` when starting)
- [ ] Test: Forgot password → send code → reset password → log in
