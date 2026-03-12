# How to Run and Test the Time Tracker App

Follow these steps in order. You need the **backend** running first, then the **mobile** app.

---

## Prerequisites

- **Python 3.9+** (for Django backend)
- **Node.js 18+** and **npm** (for React Native / Expo)
- **iOS Simulator** (Xcode on Mac) and/or **Android Emulator** (Android Studio), or a physical device

---

## Step 1: Start the Django backend

1. Open a terminal and go to the backend folder:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment (if you haven’t already):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies and run migrations:
   ```bash
   pip install -r requirements.txt
   python manage.py migrate
   ```

4. (Optional) Create a superuser for the admin site:
   ```bash
   python manage.py createsuperuser
   ```
   If one was already created during setup, you can skip this. You can use that account or create another (e.g. username: `admin`, password: `admin123`).

5. Start the server:
   ```bash
   python manage.py runserver
   ```
   You should see something like: `Starting development server at http://127.0.0.1:8000/`

6. **Quick backend check:** In a browser, open:
   - **Admin:** http://127.0.0.1:8000/admin/  
     Log in with your superuser. You should see Users, Time entries, PTO entries, PTO policies.
   - **API (will return 401 without a token):** http://127.0.0.1:8000/api/entries/  
     A “401 Unauthorized” or “Authentication credentials were not provided” means the API is up and correctly requiring auth.

Leave this terminal running.

---

## Step 2: Point the mobile app at the backend

- If you will use the **iOS Simulator** or **Android Emulator** on the same machine, the default is fine: the app uses `http://127.0.0.1:8000/api`.
- If you will use a **physical phone** on the same Wi‑Fi:
  1. Find your computer’s IP (e.g. Mac: System Settings → Network, or run `ipconfig getifaddr en0`).
  2. Open `mobile/src/api/client.js`.
  3. Change the first line to use your IP instead of `127.0.0.1`:
     ```js
     const BASE_URL = "http://192.168.1.XXX:8000/api";  // replace with your IP
     ```
  4. Save the file.

---

## Step 3: Start the mobile app (Expo)

1. Open a **second** terminal and go to the mobile folder:
   ```bash
   cd mobile
   ```

2. Install dependencies (if you haven’t already):
   ```bash
   npm install
   ```

3. Start Expo:
   ```bash
   npm start
   ```
   A development server and a QR code will appear.

4. Run the app:
   - **iOS Simulator:** Press `i` in the terminal (or scan QR with Expo Go and choose “Run on iOS simulator” if prompted).
   - **Android Emulator:** Press `a` in the terminal.
   - **Physical device:** Install “Expo Go” from the App Store or Play Store, then scan the QR code with your camera (iOS) or the Expo Go app (Android). Ensure the device is on the same Wi‑Fi and that you set `BASE_URL` to your computer’s IP as in Step 2.

The app should load and show the **Login** screen.

---

## Step 4: Test that it’s working

### 4.1 Auth

1. Tap **“Don’t have an account? Register”**.
2. Register: choose a username, email, and password (min 8 characters), then tap **Register**.
3. You should be taken to the main app (tabs: Time, Entries, PTO, Settings).
4. Tap **Settings** → **Log out**.
5. Log in again with the same username and password. You should be back on the main tabs.

If registration and login both work, auth and the backend are working.

### 4.2 Time (stopwatch and today)

1. Go to the **Time** tab.
2. Optionally enter a description, then tap **Start**. The stopwatch should run.
3. Tap **Stop**. The entry should appear under “Today’s Summary” and “Today’s Entries”.
4. Check that “Today’s Summary” shows total time and entry count.

### 4.3 Entries

1. Go to the **Entries** tab.
2. You should see the entry you just created (and any others), grouped by date.
3. Tap **Past week** to filter; tap **All** to show everything again.
4. Tap the circle on an entry to toggle **completed** (checkmark).
5. Tap **Delete** on an entry and confirm; it should disappear after refresh.

### 4.4 PTO

1. Go to the **PTO** tab.
2. Leave the date as today (or change it), pick a type (e.g. Vacation), optionally add notes.
3. Tap **Save PTO**. The new PTO day should appear in the list and the year totals (e.g. Vacation: 1/15) should update.
4. Delete a PTO entry with **Delete** and confirm.

### 4.5 Settings

1. Go to **Settings**.
2. Confirm it shows “Logged in as” and your username.
3. Toggle **Dark mode** and confirm the app theme changes.
4. Use **Log out** to return to the Login screen.

---

## Step 5: Optional – test the admin portal

1. In a browser, go to http://127.0.0.1:8000/admin/
2. Log in with your **superuser** account (e.g. `admin` / `admin123`).
3. Open **Core** → **Time entries**. You should see the time entries you created in the app (they are tied to the user you registered with).
4. Open **Core** → **PTO entries** and see the PTO days you added.
5. Open **Core** → **PTO policies**. You can add a default policy (leave “Year” empty) to set vacation/sick/personal limits; the mobile app will show these as “X/Y days”.

---

## Troubleshooting

| Problem | What to try |
|--------|---------------------|
| Mobile app shows “Network Error” or can’t log in | Backend must be running (`python manage.py runserver`). If on a real device, set `BASE_URL` in `mobile/src/api/client.js` to your computer’s IP (e.g. `http://192.168.1.XXX:8000/api`). |
| “Authentication credentials were not provided” | You’re not logged in or the token expired. Log in again from the app. |
| Expo won’t start or “Unable to resolve module” | Run `npm install` again in `mobile/`. |
| iOS Simulator: app can’t reach 127.0.0.1 | Simulator can use `127.0.0.1`; if it still fails, try `localhost` or your Mac’s IP in `BASE_URL`. |
| Changes to backend (e.g. new API) not seen | Restart Django: stop the server (Ctrl+C) and run `python manage.py runserver` again. |

Once you can register, log in, create a time entry and a PTO entry, and see them in the app and in Django admin, the app is running and working end-to-end.
