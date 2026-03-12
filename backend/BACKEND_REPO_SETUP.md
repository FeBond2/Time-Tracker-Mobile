# Backend-only repo (override complete)

The GitHub repo (e.g. **your-username/Time-Tracker-Mobile**) has been **overwritten** so it now contains **only the backend**. The repo root is the Django project (no `backend/` subfolder; no mobile app).

---

## What was done

- Created a new history with a single commit containing only backend files at repo root: `api/`, `config/`, `core/`, `manage.py`, `requirements.txt`, `vercel.json`, `.env.example`, `.gitignore`, `README.md`.
- Force-pushed to `origin main`, so GitHub now shows only that backend content.

---

## Vercel: point to this repo

1. Go to [vercel.com](https://vercel.com) → **Dashboard** → your Time Tracker project.
2. **Settings** → **Git**.
3. The connected repo is still the same repo (same repo, now backend-only).
4. Set **Root Directory** to **.** (or leave blank). The repo root is the backend; there is no `backend` subfolder anymore.
5. Save and **Redeploy** so the next build uses the new root.

Your API URL stays the same (e.g. `https://your-project.vercel.app/api`). Use it as `EXPO_PUBLIC_API_URL` in the mobile app.

---

## Local folder note

This **TimeTrackerMobile** directory is now the backend repo: the **git** tree is backend-only at root. The **mobile/** folder is still on disk but **untracked** (it is not in the repo).

- To work on the backend: edit files at root (`manage.py`, `core/`, etc.) and push to `origin main`.
- To keep the full app (mobile + backend) under version control, use a **separate** repo (e.g. a private “TimeTrackerMobile-full”) and push the full project there; this repo stays backend-only for GitHub and Vercel.
