# Railway to Render Migration Guide

## Overview
This guide covers the migration from Railway to Render for the CalmConnect backend.

## Changes Made

### 1. Django Settings (settings.py)
- ✅ Replaced Railway domains (`.up.railway.app`) with Render domains (`.onrender.com`)
- ✅ Updated `ALLOWED_HOSTS` to use `.onrender.com`
- ✅ Updated `CSRF_TRUSTED_ORIGINS` to use `RENDER_EXTERNAL_URL`
- ✅ Updated build environment detection to recognize Render variables

### 2. Entrypoint Script (entrypoint.sh)
- ✅ Uncommented and activated `python manage.py migrate --noinput`
- ✅ Added `python manage.py collectstatic --noinput --clear` for static files

### 3. Render Configuration (render.yaml)
- ✅ Created new `render.yaml` with proper service definitions
- ✅ Configured PostgreSQL 15 database service
- ✅ Set build and start commands

## Step-by-Step Migration

### 1. Prepare Render Deployment
```bash
# Login to Render
# Create new Web Service from your GitHub repo
# Render will auto-detect render.yaml if present
```

### 2. Set Environment Variables in Render Dashboard
Set these in your web service's environment variables:

```
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=[Generate a new secure key]
OPENAI_API_KEY=[Your OpenAI API key]
GMAIL_API_CREDENTIALS=[Your Gmail credentials JSON]
GMAIL_FROM_EMAIL=your-email@gmail.com
DEFAULT_FROM_EMAIL=noreply@calmconnect.edu.ph
SERVER_EMAIL=server@calmconnect.edu.ph
SESSION_COOKIE_AGE=3600
REDIS_URL=[Optional: if using external Redis]
```

### 3. Database Migration
Render will automatically provision PostgreSQL 15 as defined in `render.yaml`.

**Important**: Before deploying, ensure:
- All data from Railway is backed up
- You've exported Railway database if needed
- Consider running migrations in a separate step

### 4. Static Files
The entrypoint now handles static file collection automatically.

### 5. Verify Deployment
After Render builds and deploys:

1. Check Render logs for any errors
2. Verify the RENDER_EXTERNAL_URL matches your domain
3. Test CSRF protection is working
4. Verify email backend is configured
5. Check WebSocket connections (Daphne should handle this)

## Environment Variables Reference

| Variable | Required | Notes |
|----------|----------|-------|
| DJANGO_DEBUG | Yes | Set to `False` in production |
| DJANGO_SECRET_KEY | Yes | Generate a new one for Render |
| DATABASE_URL | Auto | Render provides this from postgres service |
| RENDER_EXTERNAL_URL | Auto | Render provides this (your domain URL) |
| OPENAI_API_KEY | Optional | For AI feedback features |
| GMAIL_API_CREDENTIALS | Recommended | For email notifications |
| DEFAULT_FROM_EMAIL | Optional | Default is GMAIL_FROM_EMAIL |
| REDIS_URL | Optional | For external Redis caching |

## Differences from Railway

| Feature | Railway | Render |
|---------|---------|--------|
| Domain Format | `.up.railway.app` | `.onrender.com` |
| SSL | Auto (*.up.railway.app) | Auto (*.onrender.com) |
| Build Env Var | `RAILWAY_ENVIRONMENT` | `RENDER` |
| External URL | Not provided directly | `RENDER_EXTERNAL_URL` |
| Database | Auto-provisioned | Via `render.yaml` |
| Static Files | Manual collection | Via entrypoint script |

## Common Issues & Solutions

### Issue: CSRF Token Validation Failed
**Solution**: 
- Verify `RENDER_EXTERNAL_URL` is set in environment
- Check that `CSRF_TRUSTED_ORIGINS` includes your domain
- Ensure `CSRF_COOKIE_SECURE=True` only when using HTTPS

### Issue: Static Files 404
**Solution**:
- Entrypoint now runs `collectstatic` automatically
- Check `STATIC_ROOT` is set to `staticfiles/`
- Verify `STATIC_URL = '/static/'`

### Issue: Database Connection Failed
**Solution**:
- Render provision PostgreSQL first (via `render.yaml`)
- Ensure `DATABASE_URL` is set correctly
- Check PostgreSQL service is running and accessible

### Issue: Migrations Failed During Deploy
**Solution**:
- View full logs in Render dashboard
- Check database credentials
- May need to run migrations manually via console

## Rollback Plan

If issues occur during migration:

1. Keep Railway service running until Render is verified
2. DNS can be pointed back to Railway if needed
3. Database backups are essential

## Next Steps

1. **Pre-deployment**:
   - Export database from Railway (optional backup)
   - Generate new `DJANGO_SECRET_KEY`
   - Configure Gmail API credentials for Render

2. **Deployment**:
   - Connect your GitHub repo to Render
   - Render will detect `render.yaml` automatically
   - Review build logs during first deployment

3. **Post-deployment**:
   - Test all functionality
   - Verify email notifications work
   - Monitor Render dashboard logs
   - Update DNS if ready to fully switch

## Additional Resources

- [Render Django Guide](https://render.com/docs/deploy-django)
- [Render Environment Variables](https://render.com/docs/environment-variables)
- [Render PostgreSQL](https://render.com/docs/databases)

## Support

If you encounter issues:
1. Check Render logs in dashboard
2. Review this migration guide
3. Refer to Django documentation
4. Check Render support documentation
