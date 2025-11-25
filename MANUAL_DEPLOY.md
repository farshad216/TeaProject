# Manual Deployment Guide for Render.com

## Step-by-Step Manual Deployment Instructions

### Step 1: Verify Your GitHub Repository

1. Make sure all your code is committed and pushed to GitHub:
   ```bash
   git add .
   git commit -m "Update superuser creation command"
   git push origin main
   ```

2. Verify your `Procfile` is in the root directory and contains:
   ```
   release: python manage.py migrate --noinput && python manage.py collectstatic --noinput --clear && python manage.py create_superuser_if_none
   web: gunicorn ecommerce_project.wsgi:application --bind 0.0.0.0:$PORT
   ```

### Step 2: Go to Render Dashboard

1. Log in to [render.com](https://render.com)
2. Click on your **Dashboard**
3. Find your web service (e.g., "teaproject" or similar)
4. Click on it to open the service details

### Step 3: Check Environment Variables

1. In your service page, click on **Environment** tab (or **Settings** → **Environment Variables**)
2. Verify these variables are set:

   | Variable Name | Value | Required? |
   |--------------|-------|-----------|
   | `SECRET_KEY` | (Your Django secret key) | ✅ YES |
   | `DJANGO_SUPERUSER_USERNAME` | `admin` | ⚠️ Recommended |
   | `DJANGO_SUPERUSER_EMAIL` | `admin@example.com` | ⚠️ Recommended |
   | `DJANGO_SUPERUSER_PASSWORD` | (Your password) | ✅ YES |
   | `DEBUG` | `False` | ⚠️ Recommended |

3. **If any are missing, add them:**
   - Click **Add Environment Variable**
   - Enter the name and value
   - Click **Save Changes**

### Step 4: Check Build and Start Commands

1. Go to **Settings** tab
2. Scroll to **Build & Deploy** section
3. Check these fields:

   **Root Directory:**
   ```
   (Leave empty)
   ```

   **Build Command:**
   ```
   pip install -r requirements.txt
   ```
   OR leave empty (Render will use Procfile)

   **Start Command:**
   ```
   gunicorn ecommerce_project.wsgi:application --bind 0.0.0.0:$PORT
   ```
   OR leave empty (Render will use Procfile)

### Step 5: Manual Deploy

1. In your service page, look for **Manual Deploy** section (usually at the top)
2. Click the dropdown next to **Manual Deploy**
3. Select **Clear build cache & deploy**
4. Click **Deploy latest commit** (or similar button)
5. Wait for deployment to start

### Step 6: Monitor the Deployment

1. Click on **Logs** tab
2. Watch the deployment process. You should see:

   **Build Phase:**
   ```
   ==> Installing dependencies...
   Collecting Django...
   Successfully installed Django-4.2.26 ...
   ```

   **Release Phase (IMPORTANT - This runs migrations and creates superuser):**
   ```
   ==> Running release command...
   Operations to perform:
     Apply all migrations: admin, auth, contenttypes, products, sessions
   Running migrations:
     Applying products.0001_initial... OK
     Applying products.0002_homepage... OK
     ...
   Collecting static files...
   ...
   Successfully created superuser: admin (is_staff=True, is_superuser=True)
   ```

   **Web Phase:**
   ```
   ==> Starting service...
   [INFO] Starting gunicorn...
   ```

### Step 7: Verify Superuser Creation

In the logs, look for one of these messages:
- ✅ `Successfully created superuser: admin (is_staff=True, is_superuser=True)`
- ✅ `Superuser already exists. Skipping creation.`
- ✅ `Successfully upgraded existing user to superuser: admin`

**If you see an error instead:**
- ❌ `DJANGO_SUPERUSER_PASSWORD not set...` → Add the environment variable
- ❌ `Error creating superuser: ...` → Check the error message

### Step 8: Test Admin Login

1. Once deployment is complete, go to: `https://teaproject.onrender.com/admin/`
2. Use these credentials:
   - **Username:** The value from `DJANGO_SUPERUSER_USERNAME` (or "admin" if not set)
   - **Password:** The value from `DJANGO_SUPERUSER_PASSWORD`

## Troubleshooting

### If Release Command Doesn't Run

If you don't see "Running release command..." in logs:

1. **Option A: Add migrations to Build Command**
   - Go to **Settings** → **Build Command**
   - Change to:
     ```
     pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput --clear && python manage.py create_superuser_if_none
     ```
   - Click **Save Changes**
   - Redeploy

2. **Option B: Verify Procfile**
   - Make sure `Procfile` is in the root of your repository
   - Make sure it's committed to Git
   - Check that it's named exactly `Procfile` (capital P, no extension)

### If Superuser Still Not Created

1. **Check Environment Variables:**
   - Go to **Environment** tab
   - Verify `DJANGO_SUPERUSER_PASSWORD` is set
   - Make sure there are no extra spaces in the value

2. **Check Logs for Errors:**
   - Look for any red error messages
   - Share the error message if you need help

3. **Try Creating Manually (if you have shell access):**
   - If you upgrade to a paid plan, you can use shell access
   - Otherwise, the automatic command should work

### If You See "Superuser already exists" but Can't Login

1. The user might exist but password might be wrong
2. **Solution:** Delete the user and redeploy:
   - If you have shell access: `python manage.py shell` → `User.objects.filter(username='admin').delete()`
   - Otherwise, the updated command should upgrade existing users

## Quick Checklist

Before deploying, make sure:
- [ ] All code is pushed to GitHub
- [ ] `Procfile` exists in root directory
- [ ] `SECRET_KEY` environment variable is set
- [ ] `DJANGO_SUPERUSER_PASSWORD` environment variable is set
- [ ] `DJANGO_SUPERUSER_USERNAME` is set (or will default to "admin")
- [ ] Build Command is set (or Procfile will be used)
- [ ] Start Command is set (or Procfile will be used)

After deploying:
- [ ] Check logs for "Running release command..."
- [ ] Check logs for "Successfully created superuser..."
- [ ] Test admin login at `/admin/`

## Need Help?

If you're still having issues:
1. Copy the full logs from the **Logs** tab
2. Check what error messages appear
3. Verify all environment variables are set correctly
4. Make sure the `Procfile` is correct and committed to Git

