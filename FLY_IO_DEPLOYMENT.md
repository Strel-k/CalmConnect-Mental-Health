# Fly.io Deployment Guide for CalmConnect

## Prerequisites
- Fly.io account
- `flyctl` installed
- Docker installed locally

## Step 1: Initialize Fly.io App
```bash
fly launch --no-deploy
```

## Step 2: Set up PostgreSQL Database
```bash
fly postgres create
# Follow prompts to create database
# Note the DATABASE_URL provided
```

## Step 3: Set up Redis (for WebSockets)
```bash
fly redis create
# Note the REDIS_URL provided
```

## Step 4: Configure Secrets
```bash
fly secrets set DJANGO_SECRET_KEY="your-very-secure-secret-key-here"
fly secrets set OPENAI_API_KEY="your-openai-api-key"
fly secrets set EMAIL_HOST_USER="your-gmail@gmail.com"
fly secrets set EMAIL_HOST_PASSWORD="your-app-password"
```

## Step 5: Update fly.toml
Edit `fly.toml` and replace:
- `your-fly-app-url.fly.dev` with your actual Fly.io app URL
- `your-production-secret-key-here` with a secure secret key

## Step 6: Deploy Application
```bash
fly deploy
```

## Step 7: Run Database Migrations
```bash
fly ssh console
# Inside the console:
python manage.py migrate
```

## Step 8: Load Production Data
```bash
# Still in fly ssh console:
python manage.py loaddata production_data.json
```

## Step 9: Create Superuser
```bash
# In fly ssh console:
python manage.py createsuperuser
```

## Step 10: Verify Deployment
- Visit your Fly.io app URL
- Check `/health/` endpoint
- Test WebSocket connections
- Verify email sending

## Environment Variables Reference
The app expects these environment variables (set via `fly secrets set`):

- `DATABASE_URL` (auto-set by Fly.io Postgres)
- `REDIS_URL` (auto-set by Fly.io Redis)
- `DJANGO_SECRET_KEY`
- `OPENAI_API_KEY`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`

## Troubleshooting
- Check logs: `fly logs`
- SSH access: `fly ssh console`
- Database issues: Verify DATABASE_URL is set correctly
- WebSocket issues: Verify REDIS_URL is set correctly