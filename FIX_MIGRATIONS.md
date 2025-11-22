# Fix: Database Migrations Not Running on Render

## Problem
Error: `django.db.utils.OperationalError: no such table: products_homepage`

This means database migrations haven't been applied on Render.

## Solution

### Option 1: Manual Migration via Build Command (Recommended)

1. Go to your Render dashboard
2. Click on your web service
3. Go to **Settings** tab
4. Find **Build Command** field
5. Change it to:
   ```
   pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput --clear
   ```
6. Click **Save Changes**
7. This will trigger a new deployment with migrations

### Option 2: Verify Procfile Release Command

Your `Procfile` should have:
```
release: python manage.py migrate --noinput && python manage.py collectstatic --noinput --clear && python manage.py create_superuser_if_none
web: gunicorn ecommerce_project.wsgi:application --bind 0.0.0.0:$PORT
```

**Important:** Make sure your `Procfile` is:
- In the root directory of your repository
- Named exactly `Procfile` (capital P, no extension)
- Committed to your Git repository

### Option 3: Check Render Logs

1. Go to Render dashboard → Your service → **Logs** tab
2. Look for the "release" command output
3. Check if you see:
   - `Running migrations...`
   - `Operations to perform:`
   - `Applying products.0001_initial... OK`
   - etc.

If you don't see migration output, the release command isn't running.

### Option 4: Force Migration via Manual Deploy

If the above doesn't work:

1. In Render dashboard, go to **Manual Deploy**
2. Select **Clear build cache & deploy**
3. This will force a fresh build and should run migrations

## After Fixing

Once migrations run successfully, you should see in the logs:
- `Operations to perform:`
- `Applying products.0001_initial... OK`
- `Applying products.0002_homepage... OK`
- `Applying products.0003_product_image_5_product_material_orderinquiry... OK`
- `Applying products.0004_alter_product_primary_image... OK`

Then your site should work without the 500 error.

## Verify It Worked

1. Check Render logs - should see migration output
2. Visit your site - should load without 500 error
3. Visit `/admin/` - should be able to log in
4. Check database tables exist (if you have shell access)

