# Troubleshooting 500 Server Error on Render.com

## Quick Fix Steps

### Step 1: Enable DEBUG Temporarily to See the Error

1. Go to your Render.com dashboard
2. Navigate to your web service
3. Go to **Environment** tab
4. Add or update this environment variable:
   - **Name:** `DEBUG`
   - **Value:** `True`
5. Click **Save Changes** (this will trigger a redeploy)
6. Wait for deployment to complete
7. Visit your site again - you should now see the actual error message instead of "Server Error (500)"
8. **Copy the error message** and then set `DEBUG` back to `False` for security

### Step 2: Common Issues and Fixes

#### Issue 1: Missing SECRET_KEY
**Error:** `django.core.exceptions.ImproperlyConfigured: The SECRET_KEY setting must not be empty`

**Fix:**
1. Generate a secret key locally:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
2. In Render dashboard → Environment tab, add:
   - **Name:** `SECRET_KEY`
   - **Value:** (paste the generated key)

#### Issue 2: Database Not Migrated
**Error:** `django.db.utils.OperationalError: no such table`

**Fix:**
- The `Procfile` should automatically run migrations, but if it didn't:
  1. Check Render logs to see if migrations ran
  2. If not, ensure your `Procfile` has:
     ```
     release: python manage.py migrate --noinput && python manage.py collectstatic --noinput --clear && python manage.py create_superuser_if_none
     ```

#### Issue 3: Static Files Not Collected
**Error:** Static files (CSS, JS) not loading

**Fix:**
- The `Procfile` should automatically collect static files
- Check Render logs to confirm `collectstatic` ran successfully
- Ensure `STATIC_ROOT` is set in `settings.py` (already done)

#### Issue 4: Missing Environment Variables
**Error:** Various import or configuration errors

**Required Environment Variables:**
1. **SECRET_KEY** (REQUIRED)
   - Generate using the command above
2. **DJANGO_SUPERUSER_PASSWORD** (REQUIRED for admin)
   - Your admin password
3. **DJANGO_SUPERUSER_USERNAME** (Optional, defaults to "admin")
4. **DJANGO_SUPERUSER_EMAIL** (Optional, defaults to "admin@example.com")

### Step 3: Check Render Logs

1. Go to your Render dashboard
2. Click on your web service
3. Click on **Logs** tab
4. Look for error messages in red
5. Common errors to look for:
   - `ModuleNotFoundError`
   - `OperationalError`
   - `ImproperlyConfigured`
   - `TemplateDoesNotExist`

### Step 4: Verify Your Configuration

#### Procfile should contain:
```
release: python manage.py migrate --noinput && python manage.py collectstatic --noinput --clear && python manage.py create_superuser_if_none
web: gunicorn ecommerce_project.wsgi:application --bind 0.0.0.0:$PORT
```

#### Start Command in Render should be:
```
gunicorn ecommerce_project.wsgi:application --bind 0.0.0.0:$PORT
```

#### Build Command in Render should be:
```
pip install -r requirements.txt
```

### Step 5: Test Locally First

Before deploying, test locally:
```bash
# Set environment variables
export SECRET_KEY="your-secret-key-here"
export DEBUG="False"

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Test the server
python manage.py runserver
```

## Still Getting 500 Error?

1. **Enable DEBUG=True** temporarily (see Step 1)
2. **Check the error message** - it will tell you exactly what's wrong
3. **Check Render logs** for detailed error traces
4. **Verify all environment variables** are set correctly
5. **Ensure your Procfile is correct** and in the root directory

## After Fixing

1. Set `DEBUG=False` in environment variables
2. Redeploy your service
3. Test your site
