# Time Tracker MVP — Deployment Guide

You’ve already done **Step 1** (run `npx expo install` in the `mobile/` folder). Below are detailed steps for **2**, **3**, and **4**.

---

## What do Railway, Render, and VPS mean?

Right now your Django backend runs **only on your computer**. When you close the laptop or turn off the server, the app can’t reach it. To use the app on a real phone (or share it with others), the backend has to run **on the internet** 24/7. That’s what “deploy” means: put your backend on a machine that’s always on and has a public web address (like `https://my-api.railway.app`).

The three options are different **places** you can run that backend:

- **Railway** and **Render** are **hosting websites**. You sign up, connect your code (e.g. from GitHub), click a few settings, and they run your Django app for you. You don’t manage a server or install the operating system—they do it. Think of them like “renting a tiny computer in the cloud that runs only your backend.” Both have free or low-cost tiers. **Best choice if you’re new:** pick one of these (e.g. Railway) and ignore VPS for now.

- **VPS** means **Virtual Private Server**. It’s a **real (virtual) computer** you rent from a company (DigitalOcean, Linode, AWS, etc.). You get an empty machine: you install Python, your code, a web server, and HTTPS yourself. It’s flexible and cheap long-term, but you have to do more setup and maintenance. **Skip this until you’re comfortable with Railway or Render.**

**Summary:** Use **Railway**, **Render**, or **Vercel** to host your Django API with minimal experience. Railway and Render run Django as a normal server; Vercel runs it as serverless (requires Postgres). The rest of this guide assumes you pick one of these.

---

## Step 2: Deploy the backend (Django API)

The mobile app needs to talk to your API over the internet with **HTTPS**. You have to run the Django backend somewhere public and get a URL like `https://your-api.example.com`.

### Option A: Railway (simplest)

1. **Sign up:** [railway.app](https://railway.app) → Sign up (e.g. GitHub).
2. **New project:** Dashboard → **New Project** → **Deploy from GitHub repo** (connect your repo and pick the **backend** folder or the whole repo and set root to `backend`).
   - If you don’t use GitHub: **Empty project** → we’ll use Railway CLI to deploy the `backend/` folder.
3. **Set root to backend (if repo root is project root):**  
   In Railway project → **Settings** → **Root Directory** → set to `backend` (so `manage.py` and `requirements.txt` are at the root of what Railway runs).
4. **Add a database (optional but recommended):**  
   In the same project → **New** → **Database** → **PostgreSQL** (or keep SQLite for a tiny MVP; SQLite is in the repo by default).  
   If you add PostgreSQL, Railway gives you `DATABASE_URL`. In **Variables** add:
   - `DATABASE_URL` = (Railway’s Postgres URL)  
   You’d then need to switch Django to use Postgres (e.g. `dj-database-url`, `ENGINE: postgresql`). For MVP you can skip this and keep SQLite (Railway’s filesystem is ephemeral, so data can be lost on redeploy; Postgres is persistent).
5. **Set environment variables** (Railway project → **Variables**):
   - `DJANGO_SECRET_KEY` = a long random string (e.g. run `python -c "import secrets; print(secrets.token_urlsafe(50))"`).
   - `DJANGO_DEBUG` = `false`.
   - `DJANGO_ALLOWED_HOSTS` = your Railway hostname, e.g. `yourapp.up.railway.app` (Railway shows it under **Settings** → **Domains** or in the deploy logs).
   - `CORS_ORIGINS` = leave empty for now, or set to `https://yourapp.up.railway.app` if you add a web front end later. For a **native mobile app** only, CORS is less critical; our backend already allows all origins when `DEBUG=true` and uses `CORS_ORIGINS` when `DEBUG=false`. Set it to your API URL if you get CORS errors: `https://yourapp.up.railway.app`.
6. **Deploy:** Railway builds and runs `python manage.py runserver` (or whatever start command you set). Set **Start Command** to something like:  
   `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`  
   and add `gunicorn` to `backend/requirements.txt` if not already there.
7. **Get the URL:** Railway assigns a URL like `https://your-project.up.railway.app`. Your **API base URL** (what the app will use) is:  
   `https://your-project.up.railway.app/api`  
   (no trailing slash). You’ll use this in Step 3.

### Option B: Render

1. **Sign up:** [render.com](https://render.com).
2. **New Web Service:** Connect your repo → choose the repo.
3. **Settings:**
   - **Root Directory:** `backend`.
   - **Build Command:** `pip install -r requirements.txt && python manage.py migrate`.
   - **Start Command:** `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`.
4. **Environment:** Add the same variables as in Railway (Step 2, items 5–6). **ALLOWED_HOSTS** should include your Render hostname, e.g. `yourapp.onrender.com`.
5. **URL:** After deploy you get something like `https://yourapp.onrender.com`. API base = `https://yourapp.onrender.com/api`.

### Option C: Vercel (serverless)

Vercel runs Django as a **serverless function**, so you get cold starts and must use an **external database** (SQLite is not persistent on Vercel). The repo is already set up for Vercel.

1. **Sign up:** [vercel.com](https://vercel.com) and connect your GitHub.
2. **Import project:** New Project → Import your repo.
3. **Set Root Directory:** In project settings, set **Root Directory** to `backend` (so `vercel.json`, `api/`, and `config/` are at the root of what Vercel builds).
4. **Add a database:** Create a Postgres database (e.g. [Vercel Postgres](https://vercel.com/storage/postgres), [Neon](https://neon.tech), or [Supabase](https://supabase.com)). You will get a `DATABASE_URL` connection string.
5. **Environment variables** (Vercel project → Settings → Environment Variables):
   - `DJANGO_SECRET_KEY` = a long random string (e.g. `python -c "import secrets; print(secrets.token_urlsafe(50))"`).
   - `DJANGO_DEBUG` = `false`.
   - `DJANGO_ALLOWED_HOSTS` = your Vercel hostname, e.g. `yourapp.vercel.app` (and any custom domain).
   - `DATABASE_URL` = your Postgres connection string (**required** on Vercel).
   - `CORS_ORIGINS` = leave empty for a mobile-only app, or set origins if you add a web front end.
6. **Run migrations:** Vercel does not run `migrate` automatically. After the first deploy, run migrations once against your `DATABASE_URL` from your machine:
   ```bash
   cd backend
   pip install -r requirements.txt
   export DATABASE_URL="your-postgres-url"
   python manage.py migrate
   ```
   Or use Vercel’s “Build Command” to run migrations during deploy (e.g. `pip install -r requirements.txt && python manage.py migrate`), though that can be slower and may require build-time DB access.
7. **Deploy:** Push to GitHub; Vercel will build and deploy. Your API base URL will be `https://yourapp.vercel.app/api` (no trailing slash). Use this as `EXPO_PUBLIC_API_URL` in Step 3.

**Note:** Serverless can have cold starts (first request after idle may be slower). For a small MVP this is usually fine. If you prefer a single long-running server and simpler DB setup, use **Railway** or **Render** (Options A or B) instead.

### Option D: Your own server (VPS)

1. On the server (e.g. Ubuntu): install Python 3, pip, and (optionally) Nginx and Postgres.
2. Clone your repo and set up a virtualenv in `backend/`:
   - `python3 -m venv venv && source venv/bin/activate`
   - `pip install -r requirements.txt gunicorn`
   - `python manage.py migrate`
3. Create a `.env` file in `backend/` from `backend/.env.example` and set:
   - `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=false`, `DJANGO_ALLOWED_HOSTS=yourdomain.com`, `CORS_ORIGINS` if needed.
4. Run Gunicorn (e.g. bound to a port or a socket). Put Nginx in front with HTTPS (Let’s Encrypt). Your API base URL will be `https://yourdomain.com/api` (or whatever path you proxy to Django).

**After Step 2 you must have:**
- A public URL that serves your Django API.
- The **exact** base URL the app should call, e.g. `https://your-project.up.railway.app/api`. We’ll call this `YOUR_API_BASE_URL` in Step 3.

---

## Step 3: Point the app at your backend (EXPO_PUBLIC_API_URL)

The app reads the API URL from the environment variable **`EXPO_PUBLIC_API_URL`**. It must be the **full base URL including `/api`**, with **no trailing slash**, e.g. `https://your-project.up.railway.app/api`.

### 3a. When running in Expo Go (development)

- **Same machine:** You can leave it unset (defaults to `http://127.0.0.1:8000/api`).
- **Phone on same Wi‑Fi:** Use your computer’s LAN IP:
  - Mac: System Settings → Network → Wi‑Fi → IP (e.g. `192.168.1.5`).
  - Then run:
    ```bash
    cd mobile
    EXPO_PUBLIC_API_URL=http://192.168.1.5:8000/api npx expo start
    ```
  - Scan the QR code with Expo Go. The app will use that URL.
- **Phone using your deployed backend:** Run:
  ```bash
  cd mobile
  EXPO_PUBLIC_API_URL=https://your-project.up.railway.app/api npx expo start
  ```
  Replace with your real API base URL.

### 3b. When building for production (EAS Build)

So that the **built** iOS/Android app uses your deployed API (and not localhost), you must set `EXPO_PUBLIC_API_URL` at **build time**.

**Option 1 — EAS Secrets (recommended)**

1. Install EAS CLI (if you haven’t): `npm install -g eas-cli`
2. Log in: `eas login`
3. From the **project root** (or from `mobile/`):
   ```bash
   cd mobile
   eas secret:create --name EXPO_PUBLIC_API_URL --value "https://your-project.up.railway.app/api" --type string
   ```
   Use your real API base URL. No trailing slash.
4. When you run `eas build`, EAS will inject this secret as an env var, and `app.config.js` will pass it into the app as `extra.apiUrl`.

**Option 2 — `eas.json` env**

1. Open `mobile/eas.json`.
2. Under the profile you use (e.g. `production` or `preview`), add an `env` block:
   ```json
   "production": {
     "ios": { "simulator": false },
     "android": { "buildType": "app-bundle" },
     "env": {
       "EXPO_PUBLIC_API_URL": "https://your-project.up.railway.app/api"
     }
   }
   ```
3. Replace the URL with your real API base. Commit only if the repo is private; for a public repo, prefer **Option 1** (secrets) so the URL isn’t in the repo.

After Step 3, any **new** build (and Expo Go runs with the env set) will use your deployed backend.

---

## Step 4: Build the app for iOS and Android (EAS Build)

EAS Build runs in the cloud and produces installable binaries (APK/AAB for Android, IPA for iOS).

### 4a. One-time setup

1. **Expo account:** Sign up at [expo.dev](https://expo.dev) if you haven’t.
2. **EAS CLI and login:**
   ```bash
   npm install -g eas-cli
   eas login
   ```
3. **Link the project (if needed):** From `mobile/`:
   ```bash
   cd mobile
   eas build:configure
   ```
   This uses or creates `eas.json` (you already have one). When asked, choose the Expo account and create/link the project.

### 4b. Android build

1. From `mobile/`:
   ```bash
   eas build --platform android --profile production
   ```
   - **production** (in your `eas.json`) builds an **AAB** (Android App Bundle) for Play Store. For local testing you can use **preview**, which builds an **APK** you can install directly:
   ```bash
   eas build --platform android --profile preview
   ```
2. Wait for the build on the Expo dashboard. When it’s done you get a link to download the **APK** (preview) or **AAB** (production).
3. **Preview APK:** Download and install on an Android device (enable “Install from unknown sources” if needed). The app will call whatever `EXPO_PUBLIC_API_URL` you set in Step 3.

### 4c. iOS build (requires Apple Developer account)

1. **Apple Developer Program:** Enroll at [developer.apple.com](https://developer.apple.com) ($99/year). Needed for real device and App Store.
2. From `mobile/`:
   ```bash
   eas build --platform ios --profile production
   ```
   Or for testing (simulator/TestFlight): `eas build --platform ios --profile preview` if you have that profile.
3. First time: EAS will ask for your Apple ID and may create a provisioning profile and certificate. Follow the prompts.
4. When the build finishes, you get a link to the **IPA**. You can install via TestFlight or submit to the App Store with `eas submit`.

### 4d. Build both at once

```bash
cd mobile
eas build --platform all --profile production
```

This queues both iOS and Android. Make sure **EXPO_PUBLIC_API_URL** is set (Step 3) for the profile you use.

---

## Checklist

- [x] **Step 1:** Run `npx expo install` in `mobile/` (you did this).
- [ ] **Step 2:** Deploy backend (Railway / Render / Vercel / VPS), get HTTPS API URL, set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=false`, `DJANGO_ALLOWED_HOSTS`, and optionally `CORS_ORIGINS` (and on Vercel: `DATABASE_URL` + run `migrate` once).
- [ ] **Step 3:** Set `EXPO_PUBLIC_API_URL` to that API base URL (e.g. `https://your-app.up.railway.app/api`) for Expo Go when testing, and for EAS Build via **EAS Secrets** or `eas.json` env.
- [ ] **Step 4:** Run `eas build --platform android` and/or `eas build --platform ios` from `mobile/` after `eas login` and (for iOS) Apple Developer setup.

If you tell me which option you use for Step 2 (Railway, Render, Vercel, or VPS), I can give you the exact variable values and start command for that option.
